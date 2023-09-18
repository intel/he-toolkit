# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

project(encoder-source LANGUAGES CXX)

cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

## Use -std=c++17 as default.
set(CMAKE_CXX_STANDARD 17)
## Disable C++ extensions
set(CMAKE_CXX_EXTENSIONS OFF)
## Require full C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Fetch gtest
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.12.1
)

FetchContent_MakeAvailable(googletest)

enable_testing()

#set(TEST_FILES tests/test_nibnaf_frac_addition.cpp tests/test_nibnaf.cpp tests/test_nibnaf_multi.cpp tests/test_sparse_poly.cpp tests/test_nibnaf_frac.cpp)
set(TEST_FILES tests/test_sparse_poly.cpp tests/test_fractional.cpp tests/test_balanced.cpp)

add_executable(tests ${TEST_FILES})

target_link_libraries(
  tests
  GTest::gtest_main
)

include(GoogleTest)
gtest_discover_tests(tests)
