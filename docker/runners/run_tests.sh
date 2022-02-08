#!/bin/bash

# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

OMP_NUM_THREADS=$(nproc) "$HOME"/he-samples/build/sample-kernels/test/unit-test
