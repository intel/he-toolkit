#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

ls

echo -e "\nIn the current directory, you will find 3 scripts:
\t1. run_sample_kernels_[palisade|seal].sh: This will run several HE sample kernels including
\t\t Matrix Multiplication and Logistic Regression. The script will display Wall time,
\t\t CPU time, and the number of iterations that were run.
\t2. run_micro_kernels_[palisade|seal].sh: This will run many HE micro kernels that span a
\t\t wide range of schemes, and display different parts of the HE pipeline from encoding
\t\t to encryption and beyond.
\t3. run_tests.sh: This will run several unit tests to confirm the validity of the above
\t\t sample kernels by comparing against the same operation in the non-HE space.
\t4. run_query_example.sh: This will run a \"Secure Query\" example allowing users
\t\t to query on a database of the 50 U.S. States while controlling (optionally) the
\t\t crypto-parameters used. When prompted, enter a State and, if present, the
\t\t corresponding City will be decoded and printed.
\t5. run_lr_example.sh: This will run a \"Logistic Regression\" (LR) example allowing users
\t\t to see a faster and more scalable method for LR in HE. Unlike the LR code available
\t\t before in the sample-kernels, this version takes extra steps to utilize as many slots
\t\t as possible in the ciphertexts.

The scripts are run as would be expected (e.g. ./run_sample_kernels_[palisade|seal].sh). When
done testing, feel free to terminate the docker with the \"exit\" command or temporarily leave
the docker Ctrl+p -> Ctrl+q, then re-enter using docker exec (see \"Docker Controls\" in
the User Guide for more information).\n\n"
