#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

OMP_NUM_THREADS=$(nproc) $HOME/projects/he-samples/build/sample-kernels/test/unit-test
