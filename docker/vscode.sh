#!/bin/bash

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

readonly user="$(whoami)"
readonly vscode_label="$user/ubuntu_he_vscode"

echo -e "\nBUILDING VSCODE DOCKERFILE..."
docker build \
  --build-arg UNAME="$user" \
  -t "$vscode_label" \
  -f Dockerfile.vscode .

echo -e "\nRUN DOCKER CONTAINER..."
docker run -d -p 8888:8888 "$vscode_label"

echo -e "\nDOCKER CONTAINER BUILT SUCCESSFULLY\nTO OPEN VSCODE NAVIGATE TO localhost:8888 IN YOUR CHOSEN BROWSER"
