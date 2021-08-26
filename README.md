# Intel Homomorphic Encryption Toolkit
The Intel Homomorphic Encryption (HE) toolkit is designed to make it fast and
easy to evaluate homomorphic encryption technology on the 3rd Generation Intel®
Xeon® Scalable Processors using libraries optimized to take advantage of the
newest Intel hardware features such as [HEXL](https://github.com/intel/hexl).
Additionally, the Intel HE-Toolkit is a great starting point for people new to
homomorphic encryption, offering numerous sample kernels showing multiple
examples of how the libraries can be used to implement common mathematical
operations using [HElib](https://github.com/homenc/HElib),
[SEAL](https://github.com/microsoft/SEAL), or
[PALISADE](https://gitlab.com/palisade/palisade-release). In addition, there
are example applications which demonstrate how HE technology can be used to
create secure applications.

## Contents
- [Intel Homomorphic Encryption Toolkit](#intel-homomorphic-encryption-toolkit)
  - [Contents](#contents)
  - [Dependencies](#dependencies)
  - [Instructions](#instructions)
    - [Docker Build (Recommended)](#docker-build-recommended)
    - [Native Build (Advanced)](#native-build-advanced)
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

Dependencies include:
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

## Instructions
There are currently two methods for building the toolkit project.

### Docker Build (Recommended)
The **recommended** method is to use the Docker build and installation which
builds the toolkit in its entirety including all HE libraries in a self
contained docker container running Ubuntu 20.04. See [here](docker) for a
detailed description on the usage and components of this build.

### Native Build (Advanced)
Alternatively, one can build the toolkit natively using the following commands

```bash
export HE_SAMPLES=$(pwd)/he-samples
cd $HE_SAMPLES
cmake -S . -B build
cmake --build build -j
```

This will build the toolkit project with the default settings. The toolkit will
download and build all three HE libraries automatically.

It is possible to pass additional options, for example:
```bash
 -DENABLE_PALISADE=ON
 -DENABLE_SEAL=ON
 -DENABLE_HELIB=OFF
```
to enable/disable building of certain HE libraries.


## Kernels
Located in `he-samples` is a collection of software components build on
Microsoft SEAL and PALISADE comprising of sample kernels for operations
performed homomorphically and example applications. The HE Samples are designed
to enable quicker evaluation of HE on Intel platforms, serve as a learning tool
for how to implement operations in different HE libraries, and provide examples
of how these operations can be used to build applications based on HE
technology for different use cases.

### Sample kernels
The [sample kernels](he-samples/sample-kernels) are for complex HE operations,
requiring multiple API calls such as Matrix Multiplication and Vector Dot
Product. Follow the link to see instructions on how to run these kernels.

### Test sample kernels
The [unit tests](he-samples/sample-kernels/test) are a selection of unit tests
meant for verifying the accuracy of the various sample kernels included in this
project.  See the link for more information.


## Examples
HE examples includes example applications built using HE technology. The
primary purpose of these examples is to serve as a showcase of different use
cases which can be implemented using HE,  as well as learning references and
starting points for further development. The toolkit currently includes the
following examples listed below.

### Secure Query
The [secure query](he-samples/examples/secure-query) example shows how it is
possible to implement a key-value database using HE and then allow a client to
perform lookups of values in the database without exposing the query to the
server hosting the database and optionally the key-value pairs in the database
as well. The secure query example is implemented using the SEAL BFV scheme. See
the link for more details and instructions on how to run this program.

### Logistic Regression
The transposed [logistic regression](he-samples/examples/logistic-regression)
example presents a scalable and fast method of logistic regression inference in
HE. Using the SEAL CKKS scheme, the example will encrypt the model (bias and
weight) and takes batches of encrypted data samples to perform the inference
all within the HE domain. See the README in the link above for usage
information.


## Contributing
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

## Contributors
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
