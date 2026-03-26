# GKit - Developer Guide

## Project Structure

```
gkit/
├── igv-report/          # IGV Report utility
│   ├── Makefile         # Test target
│   ├── pixi.toml        # Dependencies
│   └── scripts/         # Utility scripts
├── Readme.md            # Project overview
└── Readme.developer.md  # This file
```

## Running Tests

```bash
cd <utility-name>
make test
```

## Adding a New Utility

1. Create a new folder: `<utility-name>/`
2. Add `Makefile` with `test` target
3. Add `pixi.toml` with dependencies
4. Add scripts in `scripts/` folder

Example:

```bash
my-utility/
├── Makefile
├── pixi.toml
└── scripts/
    └── my_script.sh
```

## CI/CD

GitHub Actions automatically runs `make test` on modified utilities.
