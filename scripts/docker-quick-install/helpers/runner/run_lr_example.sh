#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

pushd $HOME/projects/he-samples/build/examples/logistic-regression

OMP_NUM_THREADS=$(nproc) ./lr_test

popd
