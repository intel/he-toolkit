#!/bin/bash

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

HE_SAMPLES_BUILD="$HOME/he-samples/build"
HE_SAMPLES_EXAMPLES="$HE_SAMPLES_BUILD/examples"
HE_SAMPLES_KERNELS="$HE_SAMPLES_BUILD/sample-kernels"
HE_SAMPLES_TESTS="$HE_SAMPLES_BUILD/sample-kernels/test"

run_lr_example() {
  OMP_NUM_THREADS="$(nproc)" "$HE_SAMPLES_EXAMPLES"/logistic-regression/lr_test "$@"
}

run_psi_example() {
  "$HE_SAMPLES_EXAMPLES"/psi/psi "$@"
}

run_query_example() {
  OMP_NUM_THREADS=$(nproc) "$HE_SAMPLES_EXAMPLES"/secure-query/secure-query
}

run_sample_kernels_palisade() {
  KMP_WARNINGS=0 OMP_NUM_THREADS=$(nproc) "$HE_SAMPLES_KERNELS"/sample-kernels-palisade --benchmark_min_time=2
}

run_sample_kernels_seal() {
  KMP_WARNINGS=0 OMP_NUM_THREADS=$(nproc) "$HE_SAMPLES_KERNELS"/sample-kernels-seal --benchmark_min_time=2
}

run_tests() {
  OMP_NUM_THREADS=$(nproc) "$HE_SAMPLES_TESTS"/unit-test
}

welcome_message() {
  cat << EOF

There are several bash functions sourced that you can run,
  1. run_sample_kernels_[palisade|seal]: This will run several HE sample kernels including
     Matrix Multiplication and Logistic Regression. The script will display Wall time,
     CPU time, and the number of iterations that were run.
  3. run_tests: This will run several unit tests to confirm the validity of the above
     sample kernels by comparing against the same operation in the non-HE space.
  4. run_query_example: This will run a "Secure Query" example allowing users
     to query on a database of the 50 U.S. States while controlling (optionally) the
     crypto-parameters used. When prompted, enter a State and, if present, the
     corresponding City will be decoded and printed.
  5. run_lr_example: This will run a "Logistic Regression" (LR) example allowing users
     to see a faster and more scalable method for LR in HE. Unlike the LR code available
     before in the sample-kernels, this version takes extra steps to utilize as many slots
     as possible in the ciphertexts.
  6. run_psi_example: this will execute an example that uses the HElib library and the
     BGV scheme to compute the intersection of two given sets. The program requires as input,
     a file with the client set, this is mandatory parameter, so the user must create this
     file before executing the example. Use the flag "-h" for usage information.

The bash functions are run via command line by name, e.g. run_tests. When
done testing, to terminate the docker with the "exit" command or temporarily leave
the docker Ctrl+p -> Ctrl+q, then re-enter using docker exec (see "Docker Controls" in
the User Guide for more information).


EOF
}
