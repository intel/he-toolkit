# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Defines "gflags" target

include(FetchContent)

FetchContent_Declare(
  gflags
  PREFIX gflags
  GIT_REPOSITORY https://github.com/gflags/gflags.git
  GIT_TAG v2.2.2
)
FetchContent_GetProperties(gflags)

if(NOT gflags_POPULATED)
  FetchContent_Populate(gflags)
  add_subdirectory(
      ${gflags_SOURCE_DIR}
      EXCLUDE_FROM_ALL
  )
endif()
