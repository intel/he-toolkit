# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set(GTEST_SRC
    TestLookup.cpp
    )

add_executable(unit-test main.cpp ${GTEST_SRC})

target_include_directories(unit-test PRIVATE ${UTILS_DIR} ${PSI_DIR})

find_package(GTest REQUIRED)
target_link_libraries(unit-test PRIVATE GTest::gtest)
target_link_libraries(unit-test PRIVATE helib)
