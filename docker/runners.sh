# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

HEKIT_DIR="$HOME/.hekit/components"
HEKIT_EXAMPLES="$HEKIT_DIR/examples"
HEKIT_SAMPLE_KERNELS="$HEKIT_DIR/sample-kernels"

__run_cmd() {
  (
    set -e
    eval "$*"
  )
}

run_lr_example() {
  (
    set -e
    cd "$HEKIT_EXAMPLES/logistic-regression/build"
    OMP_NUM_THREADS="$(nproc)" ./lr_test "$*"
  )
}

run_psi_example() {
  __run_cmd "$HEKIT_EXAMPLES"/psi/build/psi --server "$HEKIT_EXAMPLES"/psi/build/datasets/fruits.set "$*"
}

run_query_example() {
  (
    echo -n "Initialize SEAL BFV scheme with default parameters[Y(default)|N]: "
    read -r params
    echo -n "Input file to use for database or press enter to use default[us_state_capitals.csv]: "
    read -r database
    echo -n "Input key value to use for database query: "
    read -r query
    set -e
    OMP_NUM_THREADS="$(nproc)" "$HEKIT_EXAMPLES"/secure-query/build/secure-query <<- EOF
			${params}
			${database}
			${query}
EOF
  )
}

run_sample_kernels_palisade() {
  __run_cmd KMP_WARNINGS=0 OMP_NUM_THREADS="$(nproc)" "$HEKIT_SAMPLE_KERNELS"/palisade/build/sample-kernels-palisade --benchmark_min_time=2
}

run_sample_kernels_seal() {
  __run_cmd KMP_WARNINGS=0 OMP_NUM_THREADS="$(nproc)" "$HEKIT_SAMPLE_KERNELS"/seal/build/sample-kernels-seal --benchmark_min_time=2
}

run_tests() {
  __run_cmd OMP_NUM_THREADS="$(nproc)" "$HEKIT_SAMPLE_KERNELS"/palisade/build/test/unit-test
  __run_cmd OMP_NUM_THREADS="$(nproc)" "$HEKIT_SAMPLE_KERNELS"/seal/build/test/unit-test
}

welcome_message() {
  cat << EOF

There are several bash functions sourced that you can run,
  1. run_sample_kernels_[palisade|seal]: This will run several HE sample
     kernels including Matrix Multiplication and Logistic Regression. The
     script will display Wall time, CPU time, and the number of iterations that
     were run.
  2. run_tests: This will run several unit tests to confirm the validity of the
     above sample kernels by comparing against the same operation in the non-HE
     space.
  3. run_query_example: This will run a "Secure Query" example allowing users
     to query on a database of the 50 U.S. States while controlling
     (optionally) the crypto-parameters used. When prompted, enter a State and,
     if present, the corresponding City will be decoded and printed.
  4. run_lr_example: This will run a "Logistic Regression" (LR) example
     allowing users to see a faster and more scalable method for LR in HE.
     Unlike the LR code available before in the sample-kernels, this version
     takes extra steps to utilize as many slots as possible in the ciphertexts.
  5. run_psi_example: this will execute an example that uses the HElib library
     and the BGV scheme to compute the intersection of two given sets. The
     program requires as input, a file with the client set, this is mandatory
     parameter, so the user must create this file before executing the example.
     Use the flag "-h" for usage information.

The bash functions are run via command line by name, e.g. run_tests. When done,
you can terminate the docker container with the "exit" command or temporarily
leave the docker container typing Ctrl+p then Ctrl+q. To re-enter a detached
docker container you can reattach using \`docker attach <container-id|container-name>\`.


EOF
}
