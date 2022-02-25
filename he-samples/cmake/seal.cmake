# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#FIXME: Need logic for setting HINT DIR
set(SEAL_HINT_DIR ${HEKIT_DIR}/components/seal/v3.7.2/install
  CACHE PATH "Location of SEAL install")
message(STATUS "SEAL_HINT_DIR: ${SEAL_HINT_DIR}")

# Set path to dependencies
set(Microsoft.GSL_DIR ${HEKIT_DIR}/components/gsl/v3.1.0/install/share/cmake/Microsoft.GSL)
set(zstd_DIR ${HEKIT_DIR}/components/zstd/v1.4.5/install/lib/cmake/zstd)

find_package(SEAL
  HINTS ${SEAL_HINT_DIR}
  REQUIRED)

add_library(libseal ALIAS SEAL::seal)
