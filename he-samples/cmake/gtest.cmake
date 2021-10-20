# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Defines "gtest" target

include(FetchContent)

FetchContent_Declare(
  gtest
  PREFIX gtest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.10.0
)
FetchContent_GetProperties(gtest)

if(NOT gtest_POPULATED)
  FetchContent_Populate(gtest)
  add_subdirectory(
      ${gtest_SOURCE_DIR}
      EXCLUDE_FROM_ALL
  )
endif()
