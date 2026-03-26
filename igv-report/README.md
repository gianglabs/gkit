# IGV Report - Remote Subset Script

## Input

```
Script: ./scripts/remote_subset.sh
Parameters:
  1. REGION           - Genomic region (e.g., "1:114841797")
  2. FLANKING         - Base pairs to add on each side (default: 5000)
  3. SOURCES_CSV      - CSV file with sample names and URLs (default: data/sources.csv)
  4. OUTPUT_DIR       - Output directory path (default: subset_region_1_114841797)

Example:
  ./scripts/remote_subset.sh "1:114841797" 100 data/sources.csv output
```

### data/sources.csv Format
```csv
name,url
Illumina_HiSeq_300x,s3://giab/data/NA12878/.../HG001.hs37d5.300x.bam
10X_Chromium_v2.0,s3://giab/data/NA12878/.../NA12878_GRCh37.bam
High_Confidence_GIAB,s3://giab/release/NA12878_HG001/.../v.3.3.2_highconf_PGandRTGphasetransfer.vcf.gz
```

---

## How It Works

**Step 1: Calculate Region Boundaries**
- Input region: `1:114841797`
- Flanking: `100 bp`
- Calculate: START = 114841797 - 100 = 114841697
- Calculate: END = 114841797 + 100 = 114841897
- Final region: `1:114841697-114841897`

**Step 2: Read Source Files**
- Parse `data/sources.csv`
- Extract name and URL for each sample

**Step 3: Process Each File**
- Detect file type: `.bam` or `.vcf.gz`
- Query remote file at region `1:114841697-114841897`
  - BAM files: Use `samtools view -b <URL> <region> -o <output>`
  - VCF files: Use `bcftools view <URL> <region> -O z -o <output>`
- Check if output file has data (file size > 0)
- Create index file (.bai for BAM, .csi for VCF)

**Step 4: Generate JSON Configuration**
- Create `tracks_config.json` with all processed files
- Include file paths and index file paths for IGV

---

## Output

### Files Created in Output Directory

```
output/
├── Illumina_HiSeq_300x_1_114841797.bam           ← Subset BAM file
├── Illumina_HiSeq_300x_1_114841797.bam.bai       ← BAM index
├── 10X_Chromium_v2.0_1_114841797.bam             ← Subset BAM file
├── 10X_Chromium_v2.0_1_114841797.bam.bai         ← BAM index
├── High_Confidence_GIAB_1_114841797.vcf.gz       ← Subset VCF file
├── High_Confidence_GIAB_1_114841797.vcf.gz.csi   ← VCF index
└── tracks_config.json                             ← IGV configuration
```

### tracks_config.json Format

```json
[
  {
    "name": "Illumina_HiSeq_300x",
    "url": "output/Illumina_HiSeq_300x_1_114841797.bam",
    "indexURL": "output/Illumina_HiSeq_300x_1_114841797.bam.bai",
    "type": "alignment",
    "format": "bam",
    "height": 500
  },
  {
    "name": "High_Confidence_GIAB",
    "url": "output/High_Confidence_GIAB_1_114841797.vcf.gz",
    "indexURL": "output/High_Confidence_GIAB_1_114841797.vcf.gz.csi",
    "type": "variant",
    "format": "vcf",
    "height": 300
  }
]
```

---

## Quick Example

```bash
# Run the script
./scripts/remote_subset.sh "1:114841797" 100 data/sources.csv output

# Output:
# Region: 1:114841697-114841897
# Processing Illumina_HiSeq_300x (BAM)...
# Processing 10X_Chromium_v2.0 (BAM)...
# Processing High_Confidence_GIAB (VCF)...
# Combined tracks config saved to: output/tracks_config.json
```
