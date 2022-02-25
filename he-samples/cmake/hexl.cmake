# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#FIXME: Need logic for setting HINT DIR
set(HEXL_HINT_DIR ${HEKIT_DIR}/components/hexl/1.2.3/install
  CACHE PATH "Location of HEXL install")
message(STATUS "HEXL_HINT_DIR: ${HEXL_HINT_DIR}")

find_package(HEXL
  HINTS ${HEXL_HINT_DIR}
  REQUIRED)
