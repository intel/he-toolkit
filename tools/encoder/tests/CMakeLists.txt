# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Fetch gtest
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG release-1.12.1
)

FetchContent_MakeAvailable(googletest)

set(TEST_FILES
  test_sparse_poly.cpp
  test_fractional.cpp
  test_balanced.cpp
  test_balanced_slots.cpp
  test_encrypt.cpp
  test_ctxt_ops.cpp
)

add_executable(run_tests ${TEST_FILES})

target_link_libraries(
  run_tests
  GTest::gtest_main
  helib
)

include(GoogleTest)
gtest_discover_tests(run_tests)
