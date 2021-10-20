# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Defines "benchmark" target

include(FetchContent)

FetchContent_Declare(
  gbenchmark
  PREFIX gbenchmark
  GIT_REPOSITORY https://github.com/google/benchmark.git
  GIT_TAG v1.5.6
)
FetchContent_GetProperties(gbenchmark)

if(NOT gbenchmark_POPULATED)
  FetchContent_Populate(gbenchmark)
  add_subdirectory(
      ${gbenchmark_SOURCE_DIR}
      EXCLUDE_FROM_ALL
  )
endif()
