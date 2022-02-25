# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#FIXME: Need logic for setting HINT DIR
set(HELIB_HINT_DIR ${HEKIT_DIR}/components/helib/v2.2.1/install
  CACHE PATH "Location of HElib install")
message(STATUS "HELIB_HINT_DIR: ${HELIB_HINT_DIR}")

find_package(helib
  HINTS ${HELIB_HINT_DIR}
  REQUIRED)

add_library(libhelib ALIAS helib)
