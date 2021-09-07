# Intel Homomorphic Encryption Toolkit
The Intel Homomorphic Encryption (HE) toolkit is designed to make it fast and
easy to evaluate homomorphic encryption technology on Intel® Processors using
libraries, such as [Intel HEXL](https://github.com/intel/hexl), optimized to
take advantage of the newest Intel hardware features.  Additionally, the Intel
HE-Toolkit is a great starting point for people new to homomorphic encryption,
offering sample kernels showing multiple examples of how the libraries can be
used to implement common mathematical operations using
[Microsoft SEAL](https://github.com/microsoft/SEAL),
[PALISADE](https://gitlab.com/palisade/palisade-release), or
[HElib](https://github.com/homenc/HElib). In addition, there are example
applications which demonstrate how HE technology can be used to create secure
applications.

## Contents
- [Intel Homomorphic Encryption Toolkit](#intel-homomorphic-encryption-toolkit)
  - [Contents](#contents)
  - [Dependencies](#dependencies)
  - [Instructions](#instructions)
    - [Docker Build (Recommended)](#docker-build-recommended)
    - [Native Build](#native-build)
  - [Kernels](#kernels)
    - [Sample kernels](#sample-kernels)
    - [Test sample kernels](#test-sample-kernels)
  - [Examples](#examples)
    - [Secure Query](#secure-query)
    - [Logistic Regression](#logistic-regression)
- [Contributing](#contributing)
- [Contributors](#contributors)

## Dependencies
The toolkit has been tested on Ubuntu 20.04

Must have dependencies include:
```
cmake >= 3.13
git
pthread
patchelf
m4
g++ >= 10.0 or clang >= 10.0
python >= 3.5
virtualenv
```


Dependencies required per library include:
```
autoconf (PALISADE)
gmp >= 6.2.1 (HElib)
NTL >= 11.5.1 (HElib)
```

## Instructions
There are currently two methods for building the toolkit project.

### Docker Build (Recommended)
The **recommended** method is to use the Docker build and installation which
builds the toolkit in its entirety including all HE libraries in a
self-contained docker container running Ubuntu 20.04. See [here](docker) for a
detailed description on the usage and components of this build.

### Native Build
Alternatively, one can build the toolkit natively using the following commands

```bash
export HE_SAMPLES=$(pwd)/he-samples
cd $HE_SAMPLES
cmake -S . -B build
cmake --build build -j
```

This will build the toolkit project with the default settings. The toolkit will
download and build all three HE libraries automatically with HEXL enabled.

**Note:** You will be responsible for installing all of the required
[dependencies](#dependencies).

It is possible to pass additional options, for example:
```bash
 -DENABLE_PALISADE=ON
 -DENABLE_SEAL=ON
 -DENABLE_HELIB=OFF
```
to enable/disable building of certain HE libraries. The following table
contains the current CMake options, default values are in bold.

| CMake options            | Values   | Comments      |
|--------------------------|----------|---------------|
|`ENABLE_PALISADE`         |**ON**/OFF|Enable PALISADE|
|`ENABLE_SEAL`             |**ON**/OFF|Enable SEAL|
|`ENABLE_HELIB`            |**ON**/OFF|Enable HElib|
|`ENABLE_INTEL_HEXL`       |**ON**/OFF|Enable Intel HEXL|
|`ENABLE_ADDRESS_SANITIZER`|ON/**OFF**|Compiles and link with Address Sanitizer|
|`ENABLE_THREAD_SANITIZER` |ON/**OFF**|Compiles and link with Thread Sanitizer|
|`ENABLE_UB_SANITIZER`     |ON/**OFF**|Compiles and link with Undefined Behaviour Sanitizer|
|`SEAL_PREBUILT`           |ON/**OFF**|Use a pre-built installation of SEAL|
|`PALISADE_PREBUILT`       |ON/**OFF**|Use a pre-built installation of PALISADE|
|`HELIB_PREBUILT`          |ON/**OFF**|Use a pre-built installation of HElib|

**Note:** If using a pre-built library then you may need to use the option
`-D<SEAL|PALISADE|HELIB>_HINT_DIR=<path-to-installation>` if you have installed
them in a non-default location.


## Kernels
Located in [he-samples](he-samples) is a collection of software components
built on Microsoft SEAL and PALISADE comprising sample kernels for operations
performed homomorphically and example applications. The HE Samples are designed
to enable quicker evaluation of HE on Intel platforms, serve as a learning tool
for how to implement operations in different HE libraries, and provide examples
of how these operations can be used to build applications based on HE
technology for different use cases.

### Sample kernels
The [sample kernels](he-samples/sample-kernels) are for complex HE operations,
requiring multiple API calls such as Matrix Multiplication and Vector Dot
Product. See the [README](he-samples/sample-kernels/README.md) for
instructions.

### Test sample kernels
The [unit tests](he-samples/sample-kernels/test) are a selection of unit tests
meant for verifying the accuracy of the various sample kernels included in this
project.  See the [README](he-samples/sample-kernels/test/README.md) for
more information.


## Examples
The [examples](he-samples/examples) directory includes example applications
built using HE technology. The primary purpose of these examples is to serve as
a showcase of different use cases which can be implemented using HE. Moreover,
these can be used as learning references and starting points for further
development. The toolkit currently includes the following examples listed
below.

### Secure Query
The [secure query](he-samples/examples/secure-query) example shows how it is
possible to implement a key-value database using HE. This allows a client to
perform lookups of values in the database without exposing the query to the
server hosting the database and optionally the key-value pairs in the database
as well. The secure query example is implemented using the SEAL BFV scheme. See
the [README](he-samples/examples/secure-query/README.md) for more details and
instructions on how to run this program.

### Logistic Regression
The transposed [logistic regression](he-samples/examples/logistic-regression)
example presents a scalable and fast method of logistic regression inference in
HE. Using the SEAL CKKS scheme, the example will encrypt the model (bias and
weight) and takes batches of encrypted data samples to perform the inference
all within the HE domain. See the
[README](he-samples/examples/logistic-regression/README.md) for usage
information.


# Contributing
At this time, Intel HE Toolkit does not accept external contributions. We
encourage feedback and suggestions via
[GitHub Issues](https://github.com/intel/he-toolkit/issues) as well as via
[GitHub Discussions](https://github.com/intel/he-toolkit/discussions).

For Intel developers, ensure the [pre-commit](https://pre-commit.com) config is
active prior to contributing, i.e. run
```bash
pre-commit install
pre-commit run --all-files
```
and make sure all pre-commit checks pass.

# Contributors
The Intel contributors to this project, sorted by last name, are
  - [Paky Abu-Alam](https://www.linkedin.com/in/paky-abu-alam-89797710/)
  - [Flavio Bergamaschi](https://www.linkedin.com/in/flavio-bergamaschi)
  - [Fabian Boemer](https://www.linkedin.com/in/fabian-boemer-5a40a9102/)
  - [Jeremy Bottleson](https://www.linkedin.com/in/jeremy-bottleson-38852a7/)
  - [Jack Crawford](https://www.linkedin.com/in/jacklhcrawford/) (lead)
  - [Fillipe D.M. de Souza](https://www.linkedin.com/in/fillipe-d-m-de-souza-a8281820/)
  - [Hamish Hunt](https://www.linkedin.com/in/hamish-hunt/)
  - [Jingyi Jin](https://www.linkedin.com/in/jingyi-jin-655735/)
  - [Sejun Kim](https://www.linkedin.com/in/sejun-kim-2b1b4866/)
  - [Nir Peled](https://www.linkedin.com/in/nir-peled-4a52266/)
  - [Kylan Race](https://www.linkedin.com/in/kylanrace/)
  - [Ernesto Z Ramos](https://www.linkedin.com/in/sidezr)
  - [Gelila Seifu](https://www.linkedin.com/in/gelila-seifu/)
