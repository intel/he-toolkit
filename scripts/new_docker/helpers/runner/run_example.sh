#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

pushd $HOME/he-samples/build/examples/secure-query

OMP_NUM_THREADS=$(nproc) ./secure-query

popd
