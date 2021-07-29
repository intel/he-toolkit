A collection of kernels (micro & macro) to compare different HE libraries

# Dependencies
This has been tested on Ubuntu 18.04 & Ubuntu 20.04

A non-exhaustive list of dependencies is:
```
cmake >= 3.13
git
pthread
patchelf
m4
g++ >= 10.0 or clang >= 10.0
python >=3.5
virtualenv
```

# Build
```bash
export HE_SAMPLES=$(pwd)/he-samples
cd $HE_SAMPLES
mkdir build && cd build
cmake ..
make -j all
```

You can pass additional options:
```bash
 -DENABLE_PALISADE=OFF
 -DENABLE_SEAL=ON
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

## Logistic Regression
The logistic regression example provides a fast and scalable implementation of SEAL CKKS HE scheme based logistic regression.
It will be built whenever SEAL is enabled as part of he-toolkit build.
To run it execute
```bash
cd $HE_SAMPLES/build/examples/logistic-regression
./lr_test
```
For more detail, check [he-samples/examples/logistic-regression](he-samples/examples/logistic-regression).

# Contributing
Before making a pull request, please make sure the pre-commit config is active, i.e. run
```bash
pre-commit install
pre-commit run --all-files
```

# Contributors
The Intel contributors to this project, sorted by last name, are
  - [Paky Abu-Alam](https://www.linkedin.com/in/paky-abu-alam-89797710/)
  - [Flavio Bergamaschi](https://www.linkedin.com/in/flavio-bergamaschi-1634141/)
  - [Fabian Boemer](https://www.linkedin.com/in/fabian-boemer-5a40a9102/)
  - [Jeremy Bottleson](https://www.linkedin.com/in/jeremy-bottleson-38852a7/)
  - [Jack Crawford](https://www.linkedin.com/in/jacklhcrawford/)
  - [Fillipe D.M. de Souza](https://www.linkedin.com/in/fillipe-d-m-de-souza-a8281820/)
  - [Jingyi Jin](https://www.linkedin.com/in/jingyi-jin-655735/)
  - [Sejun Kim](https://www.linkedin.com/in/sejun-kim-2b1b4866/) (lead)
  - [Nir Peled](https://www.linkedin.com/in/nir-peled-4a52266/)
  - [Kylan Race](https://www.linkedin.com/in/kylanrace/)
  - [Ernesto Z Ramos](https://www.linkedin.com/in/sidezr)
  - [Gelila Seifu](https://www.linkedin.com/in/gelila-seifu/)
