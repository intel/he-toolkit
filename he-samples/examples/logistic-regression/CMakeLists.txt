# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

########################################################
## Logistic Regression Homomorphic Encryption Binary
########################################################

cmake_minimum_required(VERSION 3.10.2 FATAL_ERROR)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT TARGET gflags)
    find_package(gflags)
endif()
if(NOT TARGET SEAL::seal)
    find_package(SEAL 3.7 HINTS ${SEAL_HINT_DIR} REQUIRED)
endif()

set(LR_TEST_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR})
add_subdirectory(kernels)

add_executable(lr_test)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

target_link_libraries(lr_test PRIVATE SEAL::seal)

set(THREADS_PREFER_PTHREAD_FLAG ON)
target_link_libraries(lr_test PRIVATE Threads::Threads)
find_package(Threads REQUIRED)
target_link_libraries(lr_test PRIVATE lrhe_kernel)
target_link_libraries(lr_test PRIVATE gflags)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")

target_include_directories(lr_test PRIVATE ${LR_TEST_SRC_DIR})

file(GLOB LR_SRCS
        "${LR_TEST_SRC_DIR}/include/*.h"
        "${LR_TEST_SRC_DIR}/include/*.hpp"
        "${LR_TEST_SRC_DIR}/src/*.cpp"
)

target_sources(lr_test PUBLIC ${LR_SRCS})

add_subdirectory(datasets)
add_dependencies(lr_test genSyntheticData)
