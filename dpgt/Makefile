include ../common.mk
.PHONY: setup build build-cpp build-java clean prep-input run-verify

build: build-cpp build-java
	@echo "DPGT fully built!"

build-cpp: ${HOME}/.pixi/bin/pixi
	mkdir -p build
	@echo "Building C++ native libraries..."
	${HOME}/.pixi/bin/pixi run build-cpp

build-java: ${HOME}/.pixi/bin/pixi
	mkdir -p build
	@echo "Building Java JAR package..."
	cd DPGT && ${HOME}/.pixi/bin/pixi run mvn package -q -DskipTests
	@echo "Java build complete!"

test: build
	${HOME}/.pixi/bin/pixi run scripts/download.sh
	${HOME}/.pixi/bin/pixi run scripts/run_dpgt.sh

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build DPGT/target vcf_input.list results_cohort results*
	@echo "Cleaned!"

.DEFAULT_GOAL := help
