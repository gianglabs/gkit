# DPGT Cohort VCF (Pixi)

Build and run DPGT locally with Pixi, then generate a joint-genotyped cohort VCF from 3 samples.

## Quick Start

```bash
pixi install
bash run_dpgt.sh
```

## What `run_dpgt.sh` does

- checks DPGT jar and native library
- runs joint genotyping in local mode
- writes cohort VCF to an output directory

Default output example:

- `results_verify_1kgp_run_dpgt/result.chr12_111760000_111765000.0.vcf.gz`

## Optional overrides

```bash
INPUT_LIST=inputs/1kgp_3samples.list \
REFERENCE_FASTA=reference/Homo_sapiens_assembly38.fasta \
OUTPUT_DIR=results/my_run \
TARGET_REGION=chr12:111760000-111765000 \
JOBS=4 \
bash run_dpgt.sh
```

## Notes

- 1KGP 3-sample run is validated and produces cohort VCF.
- GIAB inputs may fail due to `<NON_REF>` compatibility in genotyping.
