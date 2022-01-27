# Intel HE Toolkit Docker User Guide

## Contents
- [Intel HE Toolkit Docker User Guide](#intel-he-toolkit-docker-user-guide)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Components](#components)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Steps](#steps)
  - [Running the Examples](#running-the-examples)
    - [Docker Controls](#docker-controls)
      - [Inside of the Docker Container](#inside-of-the-docker-container)
      - [Outside of the Docker Container](#outside-of-the-docker-container)
  - [Modifying the Examples](#modifying-the-examples)
  - [Common Issues](#common-issues)


## Introduction
Provided is a description of the components, usage, and installation of the
Dockerized Intel Homomorphic Encryption Toolkit. The toolkit provides a docker
environment in which one can run and modify example programs that have been
built using various Homomorphic Encryption libraries, including
[Microsoft SEAL](https://github.com/microsoft/SEAL),
[PALISADE](https://gitlab.com/palisade/palisade-release), and
[HElib](https://github.com/homenc/HElib).
All of which use the
[Intel HEXL](https://github.com/intel/hexl) library to take advantage of the
newest Intel hardware features.

## Components
The `he-toolkit/docker` directory currently contains:
- ***setup_and_run_docker.sh***: Script for building and running a docker
  container containing all HE libraries with HEXL enabled. This will be the
  main entry point for most users.
- ***basic-docker-test.sh***: Script for testing in-docker connectivity.
- ***check_dependencies.sh***: Script for checking if all required dependencies
  are installed.
- ***welcome_msg.sh***: Script which displays a welcome message upon startup of
  the docker container.
- ***Dockerfile.base***: Dockerfile recipe for building the base HE-Toolkit
  image.
- ***Dockerfile.toolkit***: Dockerfile recipe which builds a docker image
  derived from the base.
- ***env.list***: List for configuring proxy environment variables to be used
  by the docker container.
- ***utils/***: Directory containing various utility shell scripts used during
  setup.
- ***runners/***: Directory containing runner scripts for example programs and
  tests. This directory will be copied into the docker container.

## Installation
This section provides a list of pre-requisites for building and running the HE
Toolkit Docker installation as well as instructions for building the docker
container.

### Requirements
- **Docker**: Must have a working installation of Docker with network
  connectivity.  If this is not already set up then you can install Docker
  following these
  [instructions](https://docs.docker.com/engine/install/ubuntu/).
- **Supported Underlying Hardware** (Recommended): Intel HEXL will be enabled
  by default. Although Intel HEXL does not require any AVX512-enabled hardware,
  it is recommended to use a processor with at least Intel AVX512DQ support.
  For best performance, it is recommended to use processors supporting
  AVX512-IFMA52.

### Steps
To build and run the Intel HE Toolkit container, from `he-toolkit/docker` run
```bash
./setup_and_run_docker.sh
```
The installation should take a few minutes and once successful will run the
container as the current user. This will be signified with the printing of the
welcome message to the console.

If this step fails due to a missing or incorrectly configured docker
installation then you can install Docker directly from the official
[Docker website](https://docs.docker.com/get-docker/) following these
[instructions](https://docs.docker.com/engine/install/ubuntu/) to install on
Ubuntu.

## Running the Examples
After a successful install and build of the docker container, the user should
be greeted with  welcome message and be inside the container as their user in
the `~/runners` directory.

This directory will contain the following scripts:
- ***run_lr_example.sh***: This will run a Logistic Regression (LR) example
  allowing users to see a faster, more scalable method for LR in HE. Unlike the
  LR code available in the sample-kernels, this version takes extra steps to
  utilize as many slots as possible in the ciphertexts.
- ***run_query_example.sh***: This will run a Secure Query example allowing
  users to query on a database of the 50 U.S. States while controlling
  (optionally) the crypto-parameters used. When prompted, enter a State and, if
  present, the corresponding City will be decoded and printed.
- ***run_sample_kernels_palisade.sh***: This will run several HE sample kernels
  in PALISADE including Matrix Multiplication and Logistic Regression.
- ***run_sample_kernels_seal.sh***: This will run several HE sample kernels in
  SEAL including Matrix Multiplication and Logistic Regression.
- ***run_tests.sh***: This will run several unit tests to confirm the validity
  of the above sample kernels by comparing against the same operation in the
  non-HE space.

Each of these scripts can be run from the runners directory in the form of
`./<script>.sh` e.g. `./run_lr_example.sh` will run the Logistic Regression
example program.

### Docker Controls
The docker controls utilized for this toolkit are the same as the standard
docker controls:

#### Inside of the Docker Container:
- **exit**: This will exit and close the docker container. As such, the
  container would need to be rebuilt using `./setup_and_run_docker.sh`. If the
  Dockerfiles are not modified then subsequent builds should be faster as the
  existing images will cache steps.
  Alternatively, one can simply run the command `docker run -it
  <user-name>/ubuntu_he_test` to rerun the container from a previously built
  image.
- **Ctrl+P -> Ctrl+Q**: This will exit the docker container while leaving it
  running. As such the container will not need to be rerun. This is the same
  behavior if there is a connection interruption while connected to the docker.

#### Outside of the Docker Container:
- **docker ps**: This will list information about the current running docker
  containers, including the `container_id`. Use this to check if there is a
  pre-existing docker running.
- **docker exec -it <container_id> /bin/bash**: This will allow re-connection
  to a running docker container (e.g. if exited by way of `Ctrl+P -> Ctrl+Q` or
  a connection interruption). By default, this will place users in the root
  directory. So, use `cd $HOME` to switch to the user directory. Refer to
  [Running the Examples](#running-the-examples) to locate and run examples from
  this point.

## Modifying the Examples
The included source code allows for modification or existing workloads and
creations of new ones. All HE-Toolkit code can be found in
`/home/$USER/he-samples` with a directory structure directly reflected in this
repository.

HE-Samples consists of three different sub-components:
1. **Sample Kernels**: Sample kernels created through a combination of various
  micro kernels. They are meant as samples of how the  micro kernels can be
  used together. A few sample kernels (but is not limited to): Matrix
  Multiplication and Logistic Regression.
2. **Unit Tests**: A collection of unit tests meant to test the validity of the
  various sample kernels described above by comparing their results to the
  same operation in the non-HE space.
3. **Examples**: A collection of high-level examples that utilize the sample
  kernels to provide a peek into what a real-world example may look like.
  Currently three examples are implemented:
  [Secure Query](../he-samples/examples/secure-query)
  [Private Set Intersection](../he-samples/examples/psi).
  [Logistic Regression](../he-samples/examples/logistic-regression).

## Common Issues
The following table documents common issues, causes, and potential solutions.

|         Issue           |          Cause          |                  Workload                 |
|-------------------------|-------------------------|-------------------------------------------|
|**System config**: apt-get commands fail with message: `Release file for link is not valid yet (invalid for another Xd Xh Xmin Xs)`|Ubuntu system time must correct for the physical location of the system in question. If not, apt-get will fail to verify the system's certificates.|Ideally set the date and time to update automatically with: `sudo timedatectl set-ntp 1`. Or set manually with `sudo timedatectl set-time '<date> <time>'`|
|**Proxy**: Connection to Ubuntu archive, docker-hub, or general websites fail with a timeout.|Required proxy environment variables are not set up/configured properly. There are multiple proxy files that must be set, so please make sure to set all of them as required.|Set environment variables `(http_proxy & https_proxy): export http(s)_proxy=url:port`<br>Set same in the following files: `/etc/apt/apt.conf.d/proxy/conf`, `/etc/environment`|
|**Proxy**: `apt-get`, `wget`, or other connectivity necessary commands fail with `xx cannot resolve address xx`|If the host DNS is not configured to resolve addresses, then any docker fill revert to using the default Google DNS (8.8.8.8).|Enter the correct DNS address for the corporate net by editing `/etc/system/resolved.conf` accordingly.|
|**Docker**: Unsuccessful attempt at pulling docker-hub image (either hello-world image of Ubuntu 20.04 image) due to pull limit being reached.|Beginning on November 2, 2020, Docker began phasing in pull limits to reduce the amount of image pulls by anonymous Docker users.|Users may either: 1. Attempt to rerun the setup script or 2. Following the error's instructions, create a login with a Docker-hub account.|
|**Docker**: Docker connection is lost while operation inside of the Docker container.|This can be caused by many things. If the network is disconnected while the user is logged into the docker, or the terminal is closed, then they will also be removed from the running docker instance.|After logging back into the system, first check if the docker is running (see `docker ps` above). If it is, then log in with the `docker exec` command (mentioned above). If not, then rerun `setup_and_run_docker.sh`|
|**Performance**: Performance for certain samples seem to vary/run slower from inside the docker container.|Docker may cause some variance with programs that utilize a large amount of threads due to the extra level of indirection caused by the container.|While docker is meant to ease the process of setup/running, workloads may also be run outside of the docker to view full performance if necessary.|
|**Reliability**: One of the samples exits early with an error message.|We have observed in some rare cases that the code may enter an undefined state and exit early especially when running some of the more involved sample kernels.|We expect these issues to be resolved with future releases and in the meantime can be mitigated by executing the test again.|
