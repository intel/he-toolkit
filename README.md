# Intel Homomorphic Encryption Toolkit
Intel Homomorphic Encryption (HE) Toolkit is Intel's primary platform for
delivering innovation around HE with the aim of providing both the community
and industry with an intuitive entry point for Experimentation, Development and
Deployment of HE applications. Intel HE oolkit currently offers sample kernels
and example programs that demonstrate varying operations and applications that
can be built leveraging three major HE libraries [Microsoft
SEAL](https://github.com/microsoft/SEAL),
[PALISADE](https://gitlab.com/palisade/palisade-release), and
[HElib](https://github.com/homenc/HElib). Moreover, Intel HE Toolkit
demonstrates the advantages of using Intel® Processors through libraries such
as the [Intel HE Acceleration Library](https://github.com/intel/hexl) to
utilize the latest Intel hardware features.


## Contents

- [Intel Homomorphic Encryption Toolkit](#intel-homomorphic-encryption-toolkit)
  - [Contents](#contents)
  - [Dependencies](#dependencies)
  - [Setup](#setup)
  - [The hekit command](#the-hekit-command)
  - [Docker build (Recommended)](#docker-build-recommended)
  - [System build](#system-build)
  - [Kernels](#kernels)
    - [Sample kernels](#sample-kernels)
    - [Test sample kernels](#test-sample-kernels)
  - [Examples](#examples)
    - [Secure Query](#secure-query)
    - [Logistic Regression](#logistic-regression)
    - [Private Set Intersection](#private-set-intersection)
- [Contributing](#contributing)
  - [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)


## Dependencies
Intel HE toolkit has been tested on Ubuntu 20.04

Must have system dependencies for the toolkit include,
```
git
python >= 3.8
```

Further Python dependencies include,
```
toml
argcomplete (optional for tab completion)
pytest      (optional for running tests)
pytest-mock (optional for running tests)
docker      (optional for building docker containers)
```

However, to build anything useful with the toolkit, we recommend that in
addition to install the following system dependencies,

```
m4
patchelf
cmake >= 3.13
g++ >= 10.0 or clang >= 10.0
pthread
virtualenv (optional if building the Logistic Regression Example)
autoconf   (optional if using PALISADE)
gmp        (optional if using HElib)
```

## Setup
To set up the toolkit users must first initialize the `hekit` command using
```bash
git clone https://github.com/intel/he-toolkit.git
cd he-toolkit
./hekit --config default.config init
```

This will create a directory `~/.hekit` in the user's home directory and copy
the `default.config`, or other user specified config file to this location.
This directory will be where all components built and installed by `hekit` be
kept.

In addition to this, the `hekit` command will be added to the user's `PATH` so
as to enable the user to call the command from anyway on their system.

Intel HE toolkit is primarily accessible through the `hekit` command.  There
are currently two ways of interacting with the toolkit: through a Docker build;
or, directly on your system.

## The hekit command
**Move some of the kit/README to here**

The `hekit` subcommands can be used by the user to easily setup the required
environment to evaluate HE technology. See the [README](kit/README.md) for
instructions.

## Docker build (Recommended)
The **recommended** method is to use the Docker build and installation which
builds the toolkit in its entirety including all HE libraries in a
self-contained docker container running Ubuntu 20.04. This can be built through
the `hekit` command `hekit docker-build`. See [here](docker) for a detailed
description on the usage and components of this build.

## System build
Alternatively, one can build the toolkit's HE components using the following
command

```bash
hekit install recipes/default.toml
```

This will build the toolkit project with the default settings. The toolkit will
download and build all three HE libraries automatically with Intel HE
Acceleration Library enabled.

**Note:** You will be responsible for installing all of the required
[dependencies](#dependencies).

The [sample kernels](kernels) and [examples](examples) can also be built in a
similar manner using 
```bash
hekit build recipes/sample-kernels.toml
```
and
```bash
hekit build recipes/examples.toml
```
respectively.

To view a list of the components and their instances have been built/installed
through `hekit` one can execute
```bash
hekit list
```
to list each component, their instance(s) and the status of the fetch, build,
and install steps.

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
Product.  See the [README](he-samples/sample-kernels/README.md) for
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

### Private Set Intersection
The [Private Set Intersection (PSI)](he-samples/examples/psi) example computes the intersection of two
given sets. The program computes a hash value for each entry of both the client
and the server sets, then using the HElib BGV scheme, it encrypts the client
set and computes the intersection, returning all the encrypted elements that
are common to both sets. See the [README](he-samples/examples/psi/README.md)
for usage information.

# Contributing
Intel HE Toolkit welcomes external contributions through pull requests to the
`main` branch.

Please sign your commits before making a pull request. See instructions
[here](https://docs.github.com/en/github/authenticating-to-github/managing-commit-signature-verification/signing-commits)
for how to sign commits.

Before contributing, please ensure the [pre-commit](https://pre-commit.com)
checks pass, i.e. run
```bash
pre-commit install
pre-commit run --all-files
```
and make sure all pre-commit checks pass.

Also please run
```bash
pytest tests
```
to make sure the tests pass.

We encourage feedback and suggestions via
[GitHub Issues](https://github.com/intel/he-toolkit/issues) as well as via
[GitHub Discussions](https://github.com/intel/he-toolkit/discussions).


## Troubleshooting

* ```Executable `cpplint` not found```

  Make sure you install cpplint: ```pip install cpplint```.
  If you install `cpplint` locally, make sure to add it to your `PATH`.

* ```/bin/sh: 1: pre-commit: not found```

  Install `pre-commit`. More info at https://pre-commit.com/.

* When attempting to sign a commit
  ```
     error: gpg failed to sign the data
     fatal: failed to write commit object
  ```
  Try adding ```export GPG_TTY=$(tty)``` to your shell initializer script such
  as `~/.bashrc`.


# Contributors
The Intel past and present contributors to this project, sorted by last name, are
  - [Paky Abu-Alam](https://www.linkedin.com/in/paky-abu-alam-89797710/)
  - [Flavio Bergamaschi](https://www.linkedin.com/in/flavio-bergamaschi)
  - [Fabian Boemer](https://www.linkedin.com/in/fabian-boemer-5a40a9102/)
  - [Jeremy Bottleson](https://www.linkedin.com/in/jeremy-bottleson-38852a7/)
  - [Dennis Calderon Vega](https://www.linkedin.com/in/dennis-calderon-996840a9/)
  - [Jack Crawford](https://www.linkedin.com/in/jacklhcrawford/) (lead)
  - [Fillipe D.M. de Souza](https://www.linkedin.com/in/fillipe-d-m-de-souza-a8281820/)
  - [Hamish Hunt](https://www.linkedin.com/in/hamish-hunt/)
  - [Jingyi Jin](https://www.linkedin.com/in/jingyi-jin-655735/)
  - [Sejun Kim](https://www.linkedin.com/in/sejun-kim-2b1b4866/)
  - [Nir Peled](https://www.linkedin.com/in/nir-peled-4a52266/)
  - [Kylan Race](https://www.linkedin.com/in/kylanrace/)
  - [Ernesto Z Ramos](https://www.linkedin.com/in/sidezr)
  - [Gelila Seifu](https://www.linkedin.com/in/gelila-seifu/)
