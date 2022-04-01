#!/bin/bash

# Copyright (C) 2020 Intel Corporation
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
  tar -cvz --exclude he-samples/build \
    -f parts.tar.gz \
    runners \
    -C "$ROOT" \
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
  "ubuntu:20.04" \
  /bin/bash \
  /basic-docker-test.sh; then
  echo 1>&2 "In-docker connectivity failing."
  exit 1
fi

readonly user="$(whoami)"
readonly version=1.4
readonly base_label="$user/ubuntu_he_base:$version"
readonly derived_label="$user/ubuntu_he_test"

USERID="$(id -u)"
GROUPID="$(id -g)"

# Check for Mac OSX
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [ $# -eq 0 ]; then
    echo -e "\nWARNING: Detected Mac OSX... Changing UID/GID of docker user to 1000"
    USERID=1000
    GROUPID=1000
  else
    echo -e "\nWARNING: Changing UID/GID of docker user to $1"
    USERID="$1"
    GROUPID="$1"
  fi
fi

if [ -z "$(docker images -q "$base_label")" ]; then
  echo -e "\nBUILDING BASE DOCKERFILE..."
  docker build \
    --build-arg http_proxy \
    --build-arg https_proxy \
    --build-arg socks_proxy \
    --build-arg ftp_proxy \
    --build-arg no_proxy \
    --build-arg UID="$USERID" \
    --build-arg GID="$GROUPID" \
    --build-arg UNAME="$user" \
    -t "$base_label" \
    -f Dockerfile.base .
fi

echo -e "\nCLONING REPOS..."
libs_dir=libs
(# Start subshell
  mkdir -p "$libs_dir" && cd "$libs_dir"
  # Intel HE Acceleration Library
  git_clone "https://github.com/intel/hexl.git" "v1.2.3"

  # HE libs
  git_clone "https://github.com/microsoft/SEAL.git" "v3.7.2"
  git_clone "https://gitlab.com/palisade/palisade-release.git" "v1.11.6"
  git_clone "https://github.com/homenc/HElib.git" "v2.2.1"

  # SEAL dependencies
  git_clone "https://github.com/microsoft/GSL.git" "v3.1.0"
  git_clone "https://github.com/madler/zlib.git" "v1.2.11"
  git_clone "https://github.com/facebook/zstd.git" "v1.4.5"
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
