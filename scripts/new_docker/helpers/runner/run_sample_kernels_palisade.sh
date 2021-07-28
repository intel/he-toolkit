#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

export KMP_WARNINGS=0

OMP_NUM_THREADS=$(nproc) $HOME/he-samples/build/sample-kernels/sample-kernels-palisade --benchmark_min_time=2
