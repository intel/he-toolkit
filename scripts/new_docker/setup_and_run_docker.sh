#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

cat << EOF

PLEASE READ ALL OF THE FOLLOWING INSTRUCTIONS:

The following script package the he-samples code, confirm Docker functionality,
and build/run a Docker for testing several homomorphic encryption workloads.

Do note that this script has a few usage requirements:
    1. This script MUST BE RUN as a user BESIDES root.
    2. It must be run from its own base directory
    3. If you are located behind a firewall (corporate or otherwise),
    please make sure you have the proxies setup accordingly
    (e.g. environment variables: http_proxy and https_proxy are set).

EOF

read -p "If understood, press enter to continue. Otherwise, exit with Ctrl+C"
echo

if [ "$EUID" -eq 0 ]
then
    echo "Error: Please run this script as non-root"
    exit 1
fi

if [ "$(dirname $0)" != "." ]; then
    echo -e "This script MUST be run from its own base directory."
    echo -e "Please switch directory '$(dirname $0)' and run as follows:"
    echo -e "./$(basename $0)\n"
    exit 1
fi

source ./utils/dependency_checks.sh

check_dependecies \
    cmake         \
    patchelf      \
    m4            \
    g++           \
    python        \
    virtualenv

check_required_command_version "cmake --version" ">=3.13.x"
check_required_command_version "python --version" ">=3.5.x.x"
check_required_command_version "g++ --version" ">=10.0.x"

if [ ! -f "projects.tar.gz" ]; then
    echo -e "\nPACKAGING HE-SAMPLES CODE..."
    tar --exclude ../../he-samples/build -cvzf projects.tar.gz ../../he-samples
fi

if [ ! -f "helpers.tar.gz" ]; then
    echo -e "\nPACKAGING DOCKER HELPER SCRIPTS..."
    tar -cvzf helpers.tar.gz helpers
fi

echo -e "\nCHECKING DOCKER FUNCTIONALITY..."
docker run hello-world

echo -e "\nCHECKING IN-DOCKER CONNECTIVITY..."
docker run -v                                       \
    $PWD/basic-docker-test.sh:/basic-docker-test.sh \
    --env-file ./env.list                           \
    ubuntu:bionic                                   \
    /bin/bash                                       \
    /basic-docker-test.sh

version=1.3
base_label="ubuntu_he_base:$version"
derived_label="ubuntu_he_test"

if [ -z "$(docker images -q $base_label)"]; then
    echo -e "\nBUILDING BASE DOCKERFILE..."
    docker build \
        --build-arg http_proxy     \
        --build-arg https_proxy    \
        --build-arg socks_proxy    \
        --build-arg ftp_proxy      \
        --build-arg no_proxy       \
        --build-arg UID=$(id -u)   \
        --build-arg GID=$(id -g)   \
        --build-arg UNAME=$(whoami)\
        -t "$base_label" .
fi

echo -e "\nCLONING REPOS..."
if [ ! -d "SEAL/.git" ]
then
  git clone https://github.com/microsoft/SEAL.git
else
  (cd SEAL && git pull --ff-only)
fi

if [ ! -d "palisade-development/.git" ]
then
  git clone https://gitlab.com/palisade/palisade-development.git
else
  (cd palisade-development && git pull --ff-only)
fi

echo -e "\nPACKAGING LIBS..."
tar -cvzf libs.tar.gz SEAL palisade-development

echo -e "\nBUILDING TOOLKIT DOCKERFILE..."
docker build -t "$derived_label" -f toolkit.Dockerfile .

echo -e "\nRUN DOCKER CONTAINER..."
docker run -it "$derived_label"
