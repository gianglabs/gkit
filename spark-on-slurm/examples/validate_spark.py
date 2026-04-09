import sys
import time

sys.path.insert(0, ".")

from sparkhpc import sparkjob


def main() -> None:
    sj = sparkjob.sparkjob(ncores=2, cores_per_executor=2, walltime="00:10")
    cluster_id = sj.submit()
    print(f"submitted cluster_id={cluster_id} jobid={sj.jobid}")

    started = False
    deadline = time.time() + 180
    while time.time() < deadline:
        master = sj.master_url()
        if master:
            print(f"master={master}")
            started = True
            break
        time.sleep(1)

    if not started:
        sj.stop()
        raise RuntimeError("Spark master did not start in time")

    sc = None
    try:
        sc = sj.start_spark(graphframes_package=None)
        count_result = sc.parallelize(range(100)).count()
        sum_result = sc.parallelize(range(1, 11)).sum()
        print(f"count={count_result}")
        print(f"sum={sum_result}")
    finally:
        if sc is not None:
            sc.stop()
        sj.stop()
        print("cluster stopped")


if __name__ == "__main__":
    main()
