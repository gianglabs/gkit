#!/bin/bash
# DPGT runner for joint genotyping cohort VCF

set -e

PROJECT_ROOT=$(pwd)
BUILD_LIB_PATH="${PROJECT_ROOT}/build/lib"
DPGT_JAR="$(find "${PROJECT_ROOT}/DPGT/target" -name "dpgt*.jar" | head -1)"

# Defaults (override with env vars if needed)
INPUT_LIST="${INPUT_LIST:-${PROJECT_ROOT}/cohort_vcf/1KGP/gvcf_input.list}"
REFERENCE_FASTA="${REFERENCE_FASTA:-/scratch/data/nf-germline-short-read-variant-calling/benchmark/references/Homo_sapiens_assembly38.fasta}"
OUTPUT_DIR="${OUTPUT_DIR:-${PROJECT_ROOT}/cohort_vcf/1KGP/results}"
TARGET_REGION="${TARGET_REGION:-chr12:111760000-111765000}"
JOBS="${JOBS:-4}"

echo "================================"
echo "DPGT Cohort VCF Runner"
echo "================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
if [ -z "$DPGT_JAR" ] || [ ! -f "$DPGT_JAR" ]; then
    echo "ERROR: DPGT JAR not found at $DPGT_JAR"
    echo "Run 'make build' to compile DPGT first"
    exit 1
fi

if [ ! -f "$BUILD_LIB_PATH/libcdpgt.so" ]; then
    echo "ERROR: libcdpgt.so not found at $BUILD_LIB_PATH"
    echo "Run 'make build-cpp' to compile C++ libraries"
    exit 1
fi

if [ ! -f "$INPUT_LIST" ]; then
    echo "ERROR: input list not found: $INPUT_LIST"
    echo "Create it with one gVCF path per line (3-sample trio supported)."
    echo "Example existing list: ${PROJECT_ROOT}/gvcf_input.list"
    exit 1
fi

if [ ! -f "$REFERENCE_FASTA" ]; then
    echo "ERROR: reference fasta not found: $REFERENCE_FASTA"
    exit 1
fi

echo "DPGT JAR: $DPGT_JAR"
echo "C++ Library: $BUILD_LIB_PATH/libcdpgt.so"
echo "Input List: $INPUT_LIST"
echo "Reference: $REFERENCE_FASTA"
echo "Output Dir: $OUTPUT_DIR"
echo "Region: $TARGET_REGION"
echo ""

# Runtime environment
export LD_LIBRARY_PATH="$BUILD_LIB_PATH:${LD_LIBRARY_PATH}"

echo "Running DPGT joint genotyping..."
echo ""

# Some environments need explicit local filesystem implementations for Spark/Hadoop
java \
  -Dspark.hadoop.fs.file.impl=org.apache.hadoop.fs.LocalFileSystem \
  -Dspark.hadoop.fs.AbstractFileSystem.file.impl=org.apache.hadoop.fs.local.LocalFs \
  -cp "$DPGT_JAR" \
  org.bgi.flexlab.dpgt.jointcalling.JointCallingSpark \
  -i "$INPUT_LIST" \
  -r "$REFERENCE_FASTA" \
  -o "$OUTPUT_DIR" \
  -j "$JOBS" \
  -l "$TARGET_REGION" \
  --local

echo ""
echo "Run complete."
echo "Output files in: $OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 1 -type f -name "result*.vcf.gz" -print || true
