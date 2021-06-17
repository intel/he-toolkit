# Docker Quick Install
For a quick automatic setup/install, please check https://github.com/intel/he-toolkit/releases for the latest user guide. Otherwise, see below for a manual install.

# Dependencies
This has been tested on Ubuntu 18.04 & Ubuntu 20.04

A non-exhaustive list of dependencies is:
```
cmake # >= 3.13
git
pthread
patchelf
autoconf
m4
g++ #>= 10.0 or clang >= 10.0
```

# Build
```bash
export HE_SAMPLES=$(pwd)/he-samples
cd $HE_SAMPLES
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j all
```

You can pass additional options during the configure step:
```bash
 -DENABLE_PALISADE=OFF
 -DENABLE_SEAL=OFF
```
to disable building of certain HE libraries.



# Kernels
## Micro kernels
To run micro kernels, such as HE encryption, call
```bash
$HE_SAMPLES/build/micro-kernels/micro-kernels-seal
$HE_SAMPLES/build/micro-kernels/micro-kernels-palisade
```

## Sample kernels
To run larger sample kernels such as dot product, call
```bash
# Note, these will take several minutes
$HE_SAMPLES/build/sample-kernels/sample-kernels-seal
$HE_SAMPLES/build/sample-kernels/sample-kernels-palisade
```

### Test sample kernels
To run unit tests on the sample kernels, call
```bash
$HE_SAMPLES/build/sample-kernels/test/unit-test
```

# Examples

## Secure Query
The secure query example implements a simple secure database query using the SEAL BFV HE scheme.
It will be built whenever SEAL is enabled as part of he-toolkit build.
To run it execute
```bash
cd $HE_SAMPLES/build/examples/secure-query
./secure-query
```


# Contributing
At this time, Intel HE-toolkit does not accept external contributions. We encourage feedback and suggestions via [issues](https://github.com/intel/he-toolkit/issues) and [discussions](https://github.com/intel/he-toolkit/discussions).

Before making a pull request, please make sure the pre-commit config is active, i.e. run
```bash
pre-commit install
pre-commit run --all-files
```


Test change
