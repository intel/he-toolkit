#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

source ./utils/dependency_checks.sh

check_dependencies \
  cmake \
  patchelf \
  m4 \
  'clang | g++' \
  python \
  virtualenv

echo "$? missing dependencies."

# Array must be even length !
cmds_and_vers=(
  "cmake --version" ">=3.13.x"
  "python --version" ">=3.5.x"
  "clang --version" ">=10.0.x"
  "g++ --version" ">=10.0.x"
)

for ((i = 0, j = 1; j < ${#cmds_and_vers[@]}; i = i + 2, j = i + 1)); do
  if ! check_required_command_version \
    "${cmds_and_vers[$i]}" \
    "${cmds_and_vers[$j]}"; then
    echo "${cmds_and_vers[$i]% *} version must be ${cmds_and_vers[$j]}"
  fi
done
