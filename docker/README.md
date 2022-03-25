# Intel HE Toolkit Docker User Guide

## Contents
- [Intel HE Toolkit Docker User Guide](#intel-he-toolkit-docker-user-guide)
  - [Contents](#contents)
  - [Introduction](#introduction)
  - [Components](#components)
  - [Installation](#installation)
    - [Requirements](#requirements)
      - [Running the Docker Build on MacOS](#running-the-docker-build-on-macos)
    - [Steps](#steps)
  - [Running the Examples](#running-the-examples)
    - [Docker Controls](#docker-controls)
      - [Commands used inside the Docker Container:](#commands-used-inside-the-docker-container)
      - [Commands used outside of the Docker Container:](#commands-used-outside-of-the-docker-container)
  - [Modifying the Examples](#modifying-the-examples)
  - [Common Issues](#common-issues)
    - [System config](#system-config)
    - [Proxy](#proxy)
    - [Dockerhub](#dockerhub)
    - [Docker](#docker)
    - [Performance](#performance)


## Introduction
Provided is a description of the components, usage, and installation of the
Dockerized Intel HE Toolkit. The toolkit provides a docker
environment in which one can run and modify example programs that have been
built using various HE libraries, including
[Microsoft SEAL](https://github.com/microsoft/SEAL),
[PALISADE](https://gitlab.com/palisade/palisade-release), and
[HElib](https://github.com/homenc/HElib).
All of which use the [Intel HE Acceleration
Library](https://github.com/intel/hexl) library to take advantage of the newest
Intel hardware features.

## Components
The `docker` directory of Intel HE toolkit contains:
- ***README.md***: This file detailing how to build and use the Docker build
  Intel HE toolkit.
- ***basic-docker-test.sh***: Script for testing in-docker connectivity.
- ***runners.sh***: Script containing runners for example programs and
  tests.
- ***Dockerfile.base***: Dockerfile recipe for building the base for Intel HE
  Toolkit image.
- ***Dockerfile.toolkit***: Dockerfile recipe which builds a docker image
  derived from the base providing user setup and installation of toolkit
  components.
- ***Dockerfile.vscode***: Dockerfile recipe which builds a docker image
  derived from toolkit image that enables vscode server.
- ***which-files.txt***: This is an inclusive listing of the toolkit to be
  copied into the docker image.
- ***ide-config***: Directory contains configurations for vscode IDE.

## Installation
This section provides a list of pre-requisites for building and running the HE
Toolkit Docker installation as well as instructions for building the docker
container.

### Requirements
- **Docker**: Must have a working installation of Docker with network
  connectivity.  If this is not already set up then you can install Docker
  following these
  [instructions](https://docs.docker.com/engine/install/ubuntu/).
- **Supported Underlying Hardware** (Recommended): Intel HE Acceleration
  Library will be enabled by default. Although Intel HE Acceleration Library
  does not require any AVX512-enabled hardware, it is recommended to use a
  processor with at least Intel AVX512DQ support.  For best performance, it is
  recommended to use processors supporting AVX512-IFMA52.
- The docker build has been tested on,
-- Ubuntu 20.04;
-- MacOS Catalina (10.15.7).

#### Running the Docker Build on MacOS
In order to successfully run the docker build on MacOS you may be required to
run the following steps if not done so already.

1. If using Docker Desktop and you see an error such as
```bash
=> ERROR [internal] load metadata for docker.io/$USER/ubuntu_he_base:1.4
```
then open Docker Desktop, got to `Preferences`, navigate to the `Docker Engine`
tab, set the `buildkit` variable to `false`, and save this change by clicking
on `Apply & Restart`.

2. Also ensure that you allocate the docker container with at least 16GB of
  memory. This can be done via the `Resources` tab under `Preferences`.

### Steps
To build and run the Intel HE Toolkit container run
```bash
hekit docker-build
```
The installation should take a few minutes and once successful will run the
container as the current user. This will be signified with the printing of the
welcome message to the console.

If this step fails due to a missing or incorrectly configured docker
installation then you can install Docker directly from the official
[Docker website](https://docs.docker.com/get-docker/) following these
[instructions](https://docs.docker.com/engine/install/ubuntu/) to install on
Ubuntu.

**Note on macOS:** If running the docker build on Mac OSX, the UID and GID of
the user created in the docker container will both be set to 1000 by default.
To override this value the user can simply pass in the desired UID/GID as
follows
```bash
hekit docker-build --id 1234
```

## Running the Examples
After a successful install and build of the docker container, the user should
be greeted with  welcome message and be inside their user home directory.

This directory will contain the following commands that have been sourced.
- ***run_lr_example***: This will run a Logistic Regression (LR) example
  allowing users to see a faster, more scalable method for LR in HE. Unlike the
  LR code available in the sample-kernels, this version takes extra steps to
  utilize as many slots as possible in the ciphertexts.
- ***run_psi_example***: This will run a PSI example allowing users to
  perform a set intersection between a user-defined "client set" and a "server
  set" (example server sets provided). The program encrypts the client set,
  computes the intersection, and returns encrypted elements that are common to
  both sets.
- ***run_query_example***: This will run a Secure Query example allowing
  users to query on a database of the 50 U.S. States while controlling
  (optionally) the crypto-parameters used. When prompted, enter a State and, if
  present, the corresponding City will be decoded and printed.
- ***run_sample_kernels_palisade***: This will run several HE sample kernels
  in PALISADE including Matrix Multiplication and Logistic Regression.
- ***run_sample_kernels_seal***: This will run several HE sample kernels in
  SEAL including Matrix Multiplication and Logistic Regression.
- ***run_tests***: This will run several unit tests to confirm the validity
  of the above sample kernels by comparing against the same operation in the
  non-HE space.

Each command can be run from the command line simply by name e.g.
`run_lr_example` will run the Logistic Regression example program.

### Docker Controls
The docker controls utilized for Intel HE toolkit are the same as the standard
docker controls. Some tips are provided below.

#### Commands used inside the Docker Container:
- **exit**: This will exit and and stop the docker container. The containder can
  be restarted with `docker start <container_id|container_name>`. The user can
  discover their container via `docker ps -a`.
- **Ctrl+P Ctrl+Q**: This will exit the docker container while leaving it
  running. The container will not need to be rerun. This is the same
  behavior if there is a connection interruption while connected to the docker.
  The user can reattach using `docker attach <container_id|container_name>`.

#### Commands used outside of the Docker Container:
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
creations of new ones. All Intel HE Toolkit code can be found in
`/home/$USER/he-samples` with a directory structure directly reflected in this
repository.

`he-samples` consists of three different sub-components:
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
The following documents common issues, causes, and potential solutions.

### System config
apt-get command fail with message: `Release file for link is not valid yet
(invalid for another Xd Xh Xmin Xs)`. Ubuntu system time must correct for the
physical location of the system in question. If not, apt-get will fail to
verify the system's certificates. Ideally set the date and time to update
automatically with: `sudo timedatectl set-ntp 1` or set manually with `sudo
timedatectl set-time '<date> <time>'`.

### Proxy
Connection to Ubuntu archive, docker-hub, or general websites fail with a
timeout. Required proxy environment variables are not set up/configured
properly. There are multiple proxy files that must be set, so please make sure
to set all of them as required. Set environment variables `(http_proxy &
https_proxy): export http(s)_proxy=url:port`<br>Set same in the following
files: `/etc/apt/apt.conf.d/proxy/conf`, `/etc/environment`.

`apt-get`, `wget`, or other connectivity necessary commands fail with `xx
cannot resolve address xx`If the host DNS is not configured to resolve
addresses, then any docker fill revert to using the default Google DNS
(8.8.8.8). Enter the correct DNS address for the corporate net by editing
`/etc/system/resolved.conf` accordingly.

### Dockerhub
Unsuccessful attempt at pulling a dockerhub base image due to pull limit being
reached.  Beginning on November 2, 2020, Dockerhub began phasing in pull limits
to reduce the amount of image pulls by anonymous Docker users. Users may
either: 1. Attempt to rerun the setup script or 2. Following the error's
instructions, create a login with a Dockerhub account.

### Docker
Docker connection is lost while operation inside of the Docker container. This
can be due several reasons. If the network is disconnected while the user is
logged into the docker or the terminal is closed, then the user will also be
removed from the running docker instance. After logging back into the system,
check if the docker container is running with `docker ps`. If the container is
running, attach with the `docker attach` command. If the docker container is
not running restart the container with `docker start` or if the container has
been deleted create a new one with `docker run`.

### Performance
Performance for certain samples may vary from inside the docker
container. Docker may cause some variance with programs that utilize a large
amount of threads due to the extra level of indirection caused by the
container. While docker is meant to ease the process of deployment, workloads
may also be run outside of the docker to view full performance if necessary
(see [System build](###)).
