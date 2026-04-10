# DPGT Project Setup with Pixi

This directory contains DPGT (Distributed Population Genetics analysis Tool) as a git submodule, configured to build and run with pixi for dependency management.

## Project Structure

```
/scratch/data/gkit/dpgt/
├── DPGT/                      # DPGT submodule (C++ and Java)
├── cohort_vcf/               # Test data with 1KGP cohort VCFs
│   └── 1KGP/
│       └── data/
│           └── 1KGP_ALDH2_5kb.bcf  # Sample VCF file (36 KB)
├── pixi.toml                 # Pixi configuration
├── Makefile                  # Build automation
└── build_cpp.sh              # C++ build script
```

## Setup Instructions

### 1. Initialize Environment

```bash
make setup
# or manually:
pixi install
```

This creates a pixi environment with all required dependencies:
- C++ build tools (cmake, make, compilers, boost)
- Java 8 (OpenJDK)
- Build utilities (maven, pkg-config)
- System libraries (zlib, bzip2, curl, xz)

### 2. Build DPGT

#### Full Build (C++ + Java)
```bash
make build
# or
pixi run build-cpp
pixi run build-java
```

This produces:
- `build/lib/libcdpgt.so` - C++ shared library
- `DPGT/target/dpgt-1.3.2.0.jar` - Java JAR package

#### C++ Only
```bash
make build-cpp
```

#### Java Only
```bash
make build-java
```

## Working with Cohort VCF

### Sample Data Location
- **Path**: `/scratch/data/gkit/dpgt/cohort_vcf/1KGP/data/1KGP_ALDH2_5kb.bcf`
- **Size**: 36 KB (BCF format, compressed)
- **Content**: 1000 Genomes Project ALDH2 gene region (5kb window)

### Prepare Input List

```bash
make prep-input
```

This creates `vcf_input.list`:
```
/scratch/data/gkit/dpgt/cohort_vcf/1KGP/data/1KGP_ALDH2_5kb.bcf
```

### Running DPGT

To run DPGT with the cohort VCF, you need:
1. **Spark installation** (not included in pixi.toml to keep it minimal)
2. **Reference genome** (FASTA format with index)
3. **jemalloc** (optional, for memory optimization)

Example command:
```bash
export LD_LIBRARY_PATH=$(pwd)/build/lib:${LD_LIBRARY_PATH}
spark-submit \
    --master local[4] \
    --driver-memory 8g \
    --class org.bgi.flexlab.dpgt.jointcalling.JointCallingSpark \
    DPGT/target/dpgt-1.3.2.0.jar \
    -i vcf_input.list \
    -r /path/to/reference.fasta \
    -o results_cohort \
    -j 4 \
    -l ALDH2
```

## Verification

```bash
make run-verify
```

This verifies the build by displaying the DPGT help message.

## Cleaning

```bash
make clean
```

Removes all build artifacts and output directories.

## Pixi Commands

List available tasks:
```bash
pixi task list
```

Run individual tasks:
```bash
pixi run build-cpp      # Build C++ libraries
pixi run build-java     # Build Java package
pixi run prep-input     # Create VCF input list
pixi run run-local      # Show DPGT help
pixi run setup          # Display setup info
pixi run clean          # Clean artifacts
```

## Git Configuration

The DPGT submodule's `.gitmodules` has been updated to use HTTPS URLs instead of SSH:

- ❌ `git@github.com:...` (SSH)
- ✅ `https://github.com/...` (HTTPS)
- ✅ `https://gitlab.com/...` (HTTPS)

This ensures submodule initialization works without SSH keys configured.

## Troubleshooting

### Maven build hanging
If Maven appears to hang, it's likely downloading dependencies. Allow 5-10 minutes on first run.

### Missing Java home
```bash
echo $JAVA_HOME
# Should show path to Java 8 installation
```

### C++ build fails
Ensure all submodules are initialized:
```bash
cd DPGT
git submodule status  # Check status
git submodule update --init --recursive
```

### Boost not found
Verify pixi environment is activated:
```bash
pixi shell
echo $CONDA_PREFIX
cmake --version
```

## Next Steps

1. ✅ DPGT is built and ready
2. Install Spark (if not available system-wide)
3. Prepare reference genome (FASTA with .fai index)
4. Run DPGT with cohort VCF files

## Resources

- [DPGT Repository](https://github.com/BGI-flexlab/DPGT)
- [Pixi Documentation](https://pixi.sh)
- [Apache Spark Setup](https://spark.apache.org/docs/latest/index.html)
