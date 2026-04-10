#!/bin/bash
set -e

echo "Building DPGT C++ libraries..."
mkdir -p build
cd build
cmake -DCMAKE_PREFIX_PATH="${CONDA_PREFIX}" -DJAVA_INCLUDE_PATH="${JAVA_HOME}/include" ../DPGT/src/main/native/
make -j 8
echo "C++ build completed successfully!"
