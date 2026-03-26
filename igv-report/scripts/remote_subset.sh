#!/usr/bin/env bash
set -e

REGION=$1
FLANKING=${2:-5000}
SOURCES_CSV=${3:-"sources.csv"}
OUTPUT_DIR=${4:-"subset_region_$(echo $REGION | tr ':' '_')"}

[ -z "$REGION" ] && { echo "Usage: $0 <region> [flanking_size] [sources_csv] [output_dir]"; exit 1; }
[ ! -f "$SOURCES_CSV" ] && { echo "Error: Sources CSV not found: $SOURCES_CSV"; exit 1; }

CHR=$(echo $REGION | cut -d: -f1)
POS=$(echo $REGION | cut -d: -f2)

# add flanking region to subset
START=$((POS - FLANKING))
END=$((POS + FLANKING))
[ $START -lt 1 ] && START=1

mkdir -p "$OUTPUT_DIR"

echo "Region: $CHR:$START-$END"
echo "Output directory: $OUTPUT_DIR"

# create tracks information json format
TRACK_JSON="["
FIRST=true

# ============ PROCESS ALL FILES (BAM and VCF) ============
echo ""
echo "=== Processing files from $SOURCES_CSV ==="

declare -a NAMES URLS
mapfile -t lines < <(tail -n +2 "$SOURCES_CSV")
for line in "${lines[@]}"; do
    IFS=, read -r NAME URL <<< "$line"
    NAMES+=("$NAME")
    URLS+=("$URL")
done

for i in "${!NAMES[@]}"; do
    NAME="${NAMES[$i]}"
    URL="${URLS[$i]}"
    
    # Detect file type
    if [[ "$URL" == *.bam ]]; then
        FILE_TYPE="BAM"
        OUTPUT_FILE="${OUTPUT_DIR}/${NAME}_${CHR_NUM}_${POS}.bam"
    elif [[ "$URL" == *.vcf.gz ]]; then
        FILE_TYPE="VCF"
        OUTPUT_FILE="${OUTPUT_DIR}/${NAME}_${CHR_NUM}_${POS}.vcf.gz"
    else
        echo "WARNING: Unknown file type for $NAME, skipping"
        continue
    fi
    
    echo ""
    echo "Processing $FILE_TYPE: $NAME"
    
    if [ "$FILE_TYPE" = "BAM" ]; then
        # ========== BAM PROCESSING ==========
        # Subset if there are reads
        echo "Subsetting: samtools view -b '$URL' '${CHR}:${START}-${END}' -o '$OUTPUT_FILE'"
        
        if samtools view -b "$URL" "${CHR}:${START}-${END}" -o "$OUTPUT_FILE" 2>/dev/null; then
            echo "Completed subset $OUTPUT_FILE"
        else
            echo "ERROR: Failed to subset $NAME"
            rm -f "$OUTPUT_FILE"
            continue
        fi
        
        if [ -s "$OUTPUT_FILE" ]; then
            samtools index "$OUTPUT_FILE"
            if [ "$FIRST" = false ]; then            
                TRACK_JSON+=","
            fi
            FIRST=false
            
            TRACK_JSON+="
  {
    \"name\": \"${NAME}\",
    \"url\": \"${OUTPUT_FILE}\",
    \"indexURL\": \"${INDEX_FILE}\",
    \"type\": \"alignment\",
    \"format\": \"bam\",
    \"height\": 500
  }"
            echo "Complete for $OUTPUT_FILE"
        else
            echo "Output file is empty, skipping"
            rm -f "$OUTPUT_FILE"
        fi
        
    else
        # ========== VCF PROCESSING ==========
        echo "Subsetting: bcftools view '$URL' '${CHR}:${START}-${END}' -O z -o '$OUTPUT_FILE'"
        
        if bcftools view "$URL" "${CHR}:${START}-${END}" -O z -o "$OUTPUT_FILE" 2>/dev/null; then
            echo "Completed subset $OUTPUT_FILE"
        else
            echo "ERROR: Failed to subset $NAME"
            rm -f "$OUTPUT_FILE"
            continue
        fi
        
        if [ -s "$OUTPUT_FILE" ]; then
            INDEX_FILE="${OUTPUT_DIR}/${NAME}_${CHR_NUM}_${POS}.vcf.gz.csi"
            echo "Indexing: bcftools index '$OUTPUT_FILE'"
            bcftools index "$OUTPUT_FILE"
            
            if [ "$FIRST" = false ]; then
                TRACK_JSON+=","
            fi
            FIRST=false
            
            TRACK_JSON+="
  {
    \"name\": \"${NAME}\",
    \"url\": \"${OUTPUT_FILE}\",
    \"indexURL\": \"${INDEX_FILE}\",
    \"type\": \"variant\",
    \"format\": \"vcf\",
    \"height\": 300
  }"
            echo "Complete for $OUTPUT_FILE"
        else
            echo "Output file is empty, skipping"
            rm -f "$OUTPUT_FILE"
        fi
    fi
done

TRACK_JSON+="
]"

# clean index auto downloaded from remote files
rm *.bai *.tbi *.csi || echo "Already clean up"

TRACK_CONFIG="${OUTPUT_DIR}/tracks_config.json"
echo "$TRACK_JSON" > "$TRACK_CONFIG"
echo ""
echo "=== Complete ==="
echo "Combined tracks config saved to: $TRACK_CONFIG"

