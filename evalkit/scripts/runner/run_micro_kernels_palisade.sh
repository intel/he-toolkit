#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

$HOME/projects/he-toolkit/build/micro-kernels/micro-kernels-palisade --benchmark_min_time=2
