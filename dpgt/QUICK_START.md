# DPGT + Pixi Quick Reference

## Current Status ✅

- ✅ Pixi environment configured (`pixi.toml`)
- ✅ C++ libraries built (`build/lib/libcdpgt.so`)
- ✅ Git submodules initialized with HTTPS URLs
- ✅ Cohort VCF available (`/scratch/data/gkit/dpgt/cohort_vcf/1KGP/data/1KGP_ALDH2_5kb.bcf`)

## Build Status

- **C++ Build**: ✅ COMPLETE (libhts.so, libdeflate.so, libspdlog.a compiled)
- **Java Build**: Pending (Maven downloads dependencies - takes 5-10 min on first run)

## Quick Commands

### Setup (One-time)
```bash
cd /scratch/data/gkit/dpgt
make setup              # Initialize pixi environment
```

### Build
```bash
make build              # Full build (C++ + Java)
make build-cpp          # C++ only
make build-java         # Java only
```

### Prepare & Run
```bash
make prep-input         # Create vcf_input.list
./run_dpgt.sh           # Show DPGT options and requirements
```

### Cleanup
```bash
make clean              # Remove all build artifacts
```

## Project Files

| File | Purpose |
|------|---------|
| `pixi.toml` | Pixi project configuration & tasks |
| `pixi.lock` | Dependency lock file |
| `Makefile` | Build automation |
| `build_cpp.sh` | C++ build script |
| `run_dpgt.sh` | DPGT execution helper |
| `README_DPGT_PIXI.md` | Detailed documentation |
| `DPGT/` | DPGT source (git submodule) |
| `cohort_vcf/` | Test data directory |
| `build/` | Build output directory |

## Cohort VCF Location

```
/scratch/data/gkit/dpgt/cohort_vcf/1KGP/data/1KGP_ALDH2_5kb.bcf
└─ 1KGP dataset, ALDH2 gene region, 5kb window, 36 KB BCF file
```

## Dependencies Installed by Pixi

### Build Tools
- cmake, make, compilers (GCC)
- boost ≥1.74
- maven, pkg-config

### Runtime
- OpenJDK 8
- C/C++ libraries: zlib, bzip2, curl, xz
- jemalloc (memory allocator)

## Next Steps

1. **Complete Java build** (runs automatically via Maven):
   ```bash
   make build-java
   ```

2. **Prepare VCF input list**:
   ```bash
   make prep-input
   ```

3. **Install Spark** (required to run DPGT):
   ```bash
   conda install -c conda-forge pyspark
   # or follow: https://spark.apache.org/downloads.html
   ```

4. **Obtain reference genome** (FASTA + .fai index)
   - Example: GRCh38/hg38 FASTA file

5. **Run DPGT** with the helper script:
   ```bash
   ./run_dpgt.sh
   ```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Maven appears to hang" | Normal on first run (downloading deps), wait 5-10 min |
| "JAVA_HOME not set" | Run via pixi: `pixi shell` |
| "Submodule clone failed" | Already fixed (.gitmodules uses HTTPS) |
| "libcdpgt.so not found" | Run `make build-cpp` first |

## Pixi Tips

```bash
# List all available tasks
pixi task list

# Run in isolated environment (recommended)
pixi shell                    # Enter pixi environment
pixi run <task-name>          # Run specific task
pixi install --locked         # Use existing lock file

# Update dependencies
pixi update
```

## References

- [DPGT GitHub](https://github.com/BGI-flexlab/DPGT)
- [Pixi Documentation](https://pixi.sh)
- [Apache Spark Docs](https://spark.apache.org)
- [1000 Genomes Project](https://www.internationalgenome.org)
