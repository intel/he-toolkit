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

# TODO For now this is good enough.
# As the only dependency or is g++ or clang.
readonly have_gcpp="$(type -P g++)"
readonly have_clang="$(type -P clang)"
readonly gcpp_req_ver=">=10.0.x"
readonly clang_req_ver=">=10.0.x"

if [ -z "$have_gcpp" ] && [ -z "$have_clang" ]; then
  echo "g++ version must be $gcpp_req_ver or clang version must be $clang_req_ver"
elif [ -n "$have_gcpp" ] && [ -n "$have_clang" ]; then
  if ! check_required_command_version "g++ --version" "$gcpp_req_ver"; then
    echo "g++ version must be $gcpp_req_ver"
  fi
  if ! check_required_command_version "clang --version" "$clang_req_ver"; then
    echo "clang version must be $clang_req_ver"
  fi
elif [ -n "$have_gcpp" ]; then
  if ! check_required_command_version "g++ --version" "$gcpp_req_ver"; then
    echo "g++ version must be $gcpp_req_ver"
  fi
elif [ -n "$have_clang" ]; then
  if ! check_required_command_version "clang --version" "$clang_req_ver"; then
    echo "clang version must be $clang_req_ver"
  fi
else
  echo 1>&2 "This state should not be reached."
  exit 1
fi

# Array must be even length !
cmds_and_vers=(
  "cmake --version" ">=3.13.x"
  "python --version" ">=3.5.x"
)

for ((i = 0, j = 1; j < ${#cmds_and_vers[@]}; i = i + 2, j = i + 1)); do
  if ! check_required_command_version \
    "${cmds_and_vers[$i]}" \
    "${cmds_and_vers[$j]}"; then
    echo "${cmds_and_vers[$i]% *} version must be ${cmds_and_vers[$j]}"
  fi
done
