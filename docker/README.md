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
    - [Using VS Code Server](#using-vs-code-server)
  - [Running the Examples](#running-the-examples)
    - [Docker Controls](#docker-controls)
      - [Commands used inside the Docker Container](#commands-used-inside-the-docker-container)
      - [Commands used outside of the Docker Container](#commands-used-outside-of-the-docker-container)
  - [Getting Started with a Project](#getting-started-with-a-project)
  - [Common Issues](#common-issues)
    - [Permission](#permission)
    - [System config](#system-config)
    - [Proxy](#proxy)
    - [Dockerhub](#dockerhub)
    - [Docker](#docker)
    - [Rebuilding](#rebuilding)
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
  - Ubuntu 20.04;
  - MacOS Catalina (10.15.7).

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

After the image has been successfully built, the below message will be
displayed
```bash
Run container with
docker run -it <username>/ubuntu_he_toolkit:2.0.0
```
Executing this command shall start the container using `bash`.

### Using VS Code Server
The docker build optionally allows users to interact with HE Toolkit via the VS
Code IDE via [code-server](https://coder.com/docs/code-server/latest) instead
of directly via the command line. To enable this run
```bash
hekit docker-build --enable vscode
```
This will build an extra layer on top of the previous images containing a VS
Code configuration.

Once this step is successfully completed the program shall output
```bash
Successfully tagged <username>/ubuntu_he_vscode:2.0.0

RUN DOCKER CONTAINER ...
Run container with
docker run -d -p <ip addr>:<port>:8888 <username>/ubuntu_he_vscode:2.0.0
Then to open vscode navigate to <ip addr>:<port> in your chosen browser
```

This directs the user to run the VS Code enabled docker container using a
specified IP address and port using the `-p` option. The `-d` flag runs the
container in the background, allowing the user to continue using the terminal.

**Note:** To stop a container that is running in the background run
```bash
docker stop <container id>
```

After the container has been run navigate to the chosen `<ip addr>:<port>` in
your chosen browser to gain access to the Docker container via code server. You
shall initially be prompted to accept the certificate to gain access to the
webpage. Once accepted, you will be directed to the IDE.

The default workspace, `HE-WORKSPACE`, begins empty. To create a new project
see [Getting Started with a Project](#getting-started-with-a-project).

After using the terminal to create a new project you can use VS Code to build
the project by opening the Command Palette with `F1` or `Ctrl/Cmd + Shift + P`
and typing `CMake: Configure`. This will go through the steps of selecting a
compiler, CMake source directory, etc.

Alternatively, the container comes with pre-built examples and sample-kernels.
These have all been built via the `hekit` command and are located in
`$HOME/.hekit/components/<component-name>/<instance-name>`. To list the
components available, open a terminal and execute
```bash
hekit list
```
For more information on the `hekit` command see [here](../kit/README.md).

To run these pre-built projects use the provided runner commands described in
the following section [Running the Examples](#running-the-examples).


## Running the Examples
After a successful install and build of the docker container, the user should
be greeted with a welcome message and be inside their user home directory.
Within the home directory will be the `he-toolkit` repo which has already been
pre-built for the user. To run the runner commands listed below, first source
the runner script be executing
```bash
source he-toolkit/docker/runners.sh
```

The user will now have access to the following commands that have been sourced.
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

#### Commands used inside the Docker Container
- **exit**: This will exit and stop the docker container. The container can
  be restarted with `docker start <container_id|container_name>`. The user can
  discover their container via `docker ps -a`.
- **Ctrl+P Ctrl+Q**: This will exit the docker container while leaving it
  running. The container will not need to be rerun. This is the same
  behavior if there is a connection interruption while connected to the docker.
  The user can reattach using `docker attach <container_id|container_name>`.

#### Commands used outside of the Docker Container
- **docker ps**: This will list information about the current running docker
  containers, including the `container_id`. Use this to check if there is a
  pre-existing docker running.
- **docker exec -it <container_id> /bin/bash**: This will allow re-connection
  to a running docker container (e.g. if exited by way of `Ctrl+P -> Ctrl+Q` or
  a connection interruption). By default, this will place users in the root
  directory. So, use `cd $HOME` to switch to the user directory. Refer to
  [Running the Examples](#running-the-examples) to locate and run examples from
  this point.

## Getting Started with a Project
Upon initial creation of a container the user will be in an empty workspace
directory where they are free to carry out development.
To create a new project use the `hekit new` command documented
[here](../kit/README.md). This can either be used to create a generic template
for an HE project or a project based on one of the existing examples provided
by HE Toolkit.

Provided examples include:
- [Secure Query](../he-samples/examples/secure-query)
- [Private Set Intersection](../he-samples/examples/psi)
- [Logistic Regression](../he-samples/examples/logistic-regression)

## Common Issues
The following documents common issues, causes, and potential solutions.

### Permission
Running `hekit docker-build` produces a `Permission denied` error. The `hekit`
command does not allow users to call it with root privileges. Please ensure
that all necessary users are added to the `docker` user group to avoid this
issue.

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
Unsuccessful attempt at pulling a Dockerhub base image due to pull limit being
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

### Rebuilding
When rebuilding the HE Toolkit docker images using `hekit docker-build`,
`hekit` relies on a "staging" directory to load HE Toolkit files into the
docker container for use. Occasionally, this "staging" directory can become
corrupt or change and cause issues when rebuilding the docker images. Please
use `hekit docker-build --clean` to remove the staging directory and allow
`hekit` to recreate the HE Toolkit components to be copied into the docker.

### Performance
Performance for certain samples may vary from inside the docker
container. Docker may cause some variance with programs that utilize a large
amount of threads due to the extra level of indirection caused by the
container. While docker is meant to ease the process of deployment, workloads
may also be run outside of the docker to view full performance if necessary
(see [System build](../README.md#system-build)).
