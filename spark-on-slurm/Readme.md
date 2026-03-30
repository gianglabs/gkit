# Spark on Slurm (Pixi + sparkhpc)

This project runs a standalone Spark cluster **inside a Slurm job** (no Docker), then runs a small Spark example to confirm the cluster works.

It is designed to be reproducible with [Pixi](https://pixi.sh), and simple to run with `make`.

## What this setup does

When you run the example workflow:

1. Pixi creates/uses the project environment (`python`, `openjdk`, `pyspark`).
2. A Slurm batch job is submitted via `sparkhpc`.
3. Inside that Slurm allocation:
   - Spark master starts.
   - Spark worker starts using `srun`.
4. The Python driver connects to the Spark master.
5. A small test job runs (`count` and `sum`).
6. The Spark context and Slurm job are stopped.

## Key files

- `Makefile`  
  User entrypoints (`setup`, `example`, `clean`).
- `pixi.toml`  
  Environment definition and task `sparkhpc-example`.
- `sparkhpc/run_example.py`  
  End-to-end test runner: submit cluster, wait for master, run Spark actions, cleanup.
- `sparkhpc/sparkhpc/sparkjob.py`  
  Core Spark-on-Slurm orchestration logic.
- `sparkhpc/sparkhpc/templates/sparkjob.slurm.template`  
  Slurm template used to launch cluster processes inside the batch job.

## Quick start

From this directory:

```bash
make setup
make example
```

Expected output includes lines like:

- `submitted cluster_id=... jobid=...`
- `master=spark://<node>:<port>`
- `count=100`
- `sum=55`
- `cluster stopped`

## Make targets

- `make setup`  
  Installs Pixi (if missing) and installs the default Pixi environment.

- `make example`  
  Runs the full Slurm Spark smoke test via:
  - `pixi run sparkhpc-example`

- `make clean`  
  Removes local generated artifacts:
  - `sparkhpc/sparkcluster-*.log`
  - `sparkhpc/job`
  - `${HOME}/.sparkhpc*` metadata files

## How `run_example.py` works

`sparkhpc/run_example.py` performs these steps:

1. Create Spark job object:
   - `ncores=2`
   - `cores_per_executor=2`
   - `walltime="00:10"`
2. Submit Slurm job (`sj.submit()`).
3. Poll until Spark master URL is available (`sj.master_url()`).
4. Start PySpark context (`sj.start_spark(graphframes_package=None)`).
5. Run test actions:
   - `sc.parallelize(range(100)).count()`
   - `sc.parallelize(range(1, 11)).sum()`
6. Stop Spark context and Slurm job in `finally` block.

This gives deterministic pass/fail behavior and avoids leaving jobs running.

## Slurm notes

- The cluster is created as a Slurm batch job (`sbatch`) and worker processes run with `srun`.
- You can inspect jobs with:

```bash
squeue -u $USER
```

- Spark cluster logs are written in `sparkhpc/sparkcluster-<jobid>.log`.

## Troubleshooting

- **`JAVA_HOME not set`**  
  Run through Pixi (`make example` or `pixi run ...`) so Java env is provided.

- **`No module named sparkhpc` in Slurm log**  
  Ensure you run from project root; template now injects submit dir into `sys.path`.

- **Job submitted but no master URL appears**  
  Check `sparkhpc/sparkcluster-<jobid>.log` and Slurm state with `squeue`.

- **Port conflicts**  
  Spark may auto-select alternate ports if defaults are busy.

## Scope

This README describes **Spark-on-Slurm only**. HDFS/Hadoop integration is intentionally deferred for a separate step.
