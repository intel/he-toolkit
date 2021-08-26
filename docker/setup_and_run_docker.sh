#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

ROOT="$(realpath ..)"

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

read -rp "If understood, press enter to continue. Otherwise, exit with Ctrl+C"
echo

if [ "$EUID" -eq 0 ]; then
  echo "Error: Please run this script as non-root"
  exit 1
fi

if [ "$(dirname "$0")" != "." ]; then
  echo -e "This script MUST be run from its base directory."
  echo -e "Please switch directory '$(dirname "$0")' and run as follows:"
  echo -e "./$(basename "$0")\n"
  exit 1
fi

# shellcheck source=utils/gitops.sh
source utils/gitops.sh

if [ ! -f "parts.tar.gz" ]; then
  echo -e "\nPACKAGING HE-SAMPLES CODE..."
  tar -cvzf parts.tar.gz \
    runners \
    -C "$ROOT" \
    --exclude he-samples/build \
    he-samples
fi

echo -e "\nCHECKING DOCKER FUNCTIONALITY..."
if ! docker images > /dev/null; then
  echo 1>&2 "FATAL: You need docker."
fi

echo -e "\nCHECKING IN-DOCKER CONNECTIVITY..."
if ! docker run -v \
  "$PWD"/basic-docker-test.sh:/basic-docker-test.sh \
  --env-file ./env.list \
  ubuntu:bionic \
  /bin/bash \
  /basic-docker-test.sh; then
  echo 1>&2 "In-docker connectivity failing."
  exit 1
fi

readonly user="$(whoami)"
readonly version=1.3
readonly base_label="$user/ubuntu_he_base:$version"
readonly derived_label="$user/ubuntu_he_test"

if [ -z "$(docker images -q "$base_label")" ]; then
  echo -e "\nBUILDING BASE DOCKERFILE..."
  docker build \
    --build-arg http_proxy \
    --build-arg https_proxy \
    --build-arg socks_proxy \
    --build-arg ftp_proxy \
    --build-arg no_proxy \
    --build-arg UID="$(id -u)" \
    --build-arg GID="$(id -g)" \
    --build-arg UNAME="$user" \
    -t "$base_label" \
    -f Dockerfile.base .
fi

echo -e "\nCLONING REPOS..."
libs_dir=libs
(# Start subshell
  mkdir -p "$libs_dir" && cd "$libs_dir"
  # HEXL
  git_clone "https://github.com/intel/hexl.git" "1.1.0-patch"

  # HE libs
  git_clone "https://github.com/microsoft/SEAL.git" "3.6.6"
  git_clone "https://gitlab.com/palisade/palisade-release.git"

  # SEAL dependencies
  git_clone "https://github.com/microsoft/GSL.git"
  git_clone "https://github.com/madler/zlib.git"
  git_clone "https://github.com/facebook/zstd.git"
) # End subshell

echo -e "\nPACKAGING LIBS..."
tar -cvzf libs.tar.gz "$libs_dir"

echo -e "\nBUILDING TOOLKIT DOCKERFILE..."
docker build \
  --build-arg UNAME="$user" \
  -t "$derived_label" \
  -f Dockerfile.toolkit .

echo -e "\nRUN DOCKER CONTAINER..."
docker run -it "$derived_label"
