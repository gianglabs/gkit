# GLnexus Joint Genotyping Configuration

A simple configuration for performing joint genotyping of genomic variants using **GLnexus**, demonstrating cohort analysis with sample data from GIAB and 1000 Genomes Project.

## Overview

This project automates joint variant calling on gVCF files from multiple samples using GLnexus. It includes:

- **Data Download**: Automatically retrieves sample gVCF files from public cloud storage (GIAB and 1000 Genomes)
- **Joint Calling**: Performs multi-sample variant calling on the ALDH2 region (5kb) using GLnexus
- **Output Conversion**: Converts BCF output to gzip-compressed VCF format

## Quick Start

### Prerequisites

- [Pixi](https://pixi.sh/) - Package manager for reproducible environments
- Internet connectivity (for downloading sample data from cloud storage)
- AWS CLI or gsutil credentials (for accessing public datasets)

### Installation

1. Install Pixi if you haven't already:

```bash
curl -sSL https://pixi.sh/install.sh | sh
```

2. Clone or navigate to this repository:

```bash
cd /path/to/glnexus
```

### Running the Pipeline

Execute the complete joint genotyping pipeline:

```bash
make test
```

This will:

1. Install dependencies in a managed Pixi environment
2. Download gVCF files from GIAB and 1000 Genomes
3. Run GLnexus joint calling
4. Convert outputs to compressed VCF format

## Project Structure

```
glnexus/
├── joint_genotyping_cohort_vcf.sh    # Main pipeline script
├── ALDH2_5kb.bed                     # Test region (BED format)
├── Makefile                          # Build automation
├── pixi.toml                         # Dependency configuration
├── pixi.lock                         # Locked dependency versions
├── cohort_vcf/                       # Output directory structure
│   ├── GIAB/data/                    # GIAB samples output
│   └── 1KGP/data/                    # 1000 Genomes samples output
└── Readme.md                         # This file
```

## Dependencies

The pipeline uses the following tools (managed by Pixi):

- **GLnexus** (>=1.4.1, <2) - Multi-sample variant calling
- **BCFtools** (>=1.23.1, <2) - VCF/BCF manipulation
- **SAMtools** (>=1.23.1, <2) - Sequence manipulation
- **gsutil** - Google Cloud Storage access
- **google-cloud-storage** (>=2.10.0) - Cloud storage library

## Sample Data

### GIAB (Genome in a Bottle)

- HG002 (child)
- HG003 (parent 1)
- HG004 (parent 2)

Source: DeepVariant case study outputs (v1.10.0)

### 1000 Genomes Project (1KGP)

- NA21144
- NA21143
- NA21142

Source: DRAGEN v4.2.7 processed individuals

## Test Region

The pipeline analyzes the **ALDH2 region** on chromosome 12 (5kb window):

- **Chromosome**: chr12
- **Start**: 111,760,000
- **End**: 111,765,000
- **File**: ALDH2_5kb.bed

## Output Files

After running the pipeline, the following VCF files are generated:

```
cohort_vcf/GIAB/data/GIAB_ALDH2_5kb.vcf.gz      # GIAB joint calls
cohort_vcf/1KGP/data/1KGP_ALDH2_5kb.vcf.gz      # 1KGP joint calls
```

Both outputs include corresponding index files (.tbi).

## Configuration

### GLnexus Parameters

The pipeline uses the following GLnexus settings:

```bash
glnexus_cli --config DeepVariant --threads 4 --bed ALDH2_5kb.bed
```

- **Config**: DeepVariant (optimized for DeepVariant gVCF output)
- **Threads**: 4 (CPU cores for parallel processing)
- **BED region**: ALDH2_5kb.bed (limits analysis to test region)

### Customization

To modify the analysis:

1. **Change region of interest**: Edit `ALDH2_5kb.bed` with new coordinates
2. **Adjust threading**: Modify `--threads` parameter in `joint_genotyping_cohort_vcf.sh`
3. **Add more samples**: Add gsutil/aws commands and include gVCF files in the glob pattern

## Usage Examples

### Run complete pipeline

```bash
make test
```

### Manual execution

```bash
# Activate environment
pixi shell

# Run pipeline
bash joint_genotyping_cohort_vcf.sh
```

### Run specific cohort only

```bash
# GIAB only
cd cohort_vcf/GIAB/data
glnexus_cli --config DeepVariant --threads 4 --bed ../../ALDH2_5kb.bed *.g.vcf.gz > GIAB_ALDH2_5kb.bcf
```

## Troubleshooting

### Low Memory

Adjust thread count to reduce memory usage:

```bash
--threads 2  # Instead of 4
```

### File Not Found

Ensure the `cohort_vcf/GIAB/data` and `cohort_vcf/1KGP/data` directories exist. They should be created by the pipeline, but you can create them manually:

```bash
mkdir -p cohort_vcf/GIAB/data cohort_vcf/1KGP/data
```

## References

- [GLnexus Documentation](https://github.com/dnanexus-rnd/GLnexus)
- [DeepVariant Case Study](https://github.com/google/deepvariant/blob/r1.10/docs/case_study.md)
- [1000 Genomes Project](https://www.internationalgenome.org/)
- [Genome in a Bottle](https://www.nist.gov/programs/giab)

## License

This configuration is provided as-is for educational and research purposes.

## Author

nttg8100 &lt;nttg8100@gmail&gt;
