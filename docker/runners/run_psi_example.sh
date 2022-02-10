#!/bin/bash

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

pushd "$HOME"/he-samples/build/examples/psi

./psi "$@"

popd
