#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

$HOME/he-samples/build/micro-kernels/micro-kernels-seal --benchmark_min_time=2
