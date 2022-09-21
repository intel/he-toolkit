#!/bin/bash

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

progpath="${BASH_SOURCE[0]}"
if [ "$progpath" == "$0" ]; then
  echo >&2 "$progpath must be sourced"
  exit 1
fi

progdir="$(dirname "$progpath")"

CONFIG_PSI_DIR="$(realpath "$progdir")"
export CONFIG_PSI_DIR

PYTHONPATH="$PYTHONPATH:$CONFIG_PSI_DIR/scripts"
export PYTHONPATH
