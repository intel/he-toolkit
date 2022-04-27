#!/usr/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

factor {2..140000} | awk 'NF == 2 {print $NF}' > primes.txt
