# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

project(sample-kernels LANGUAGES CXX)

cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

## Use -std=c++17 as default.
set(CMAKE_CXX_STANDARD 17)
## Disable C++ extensions
set(CMAKE_CXX_EXTENSIONS OFF)
## Require full C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(SAMPLE_KERNELS_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR})

find_package (OpenMP REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

# Download gbenchmark and gtest libraries
include(../cmake/gbenchmark.cmake)
include(../cmake/gtest.cmake)

if (${ENABLE_SEAL})
  # SEAL sample kernel

  find_package(SEAL REQUIRED)

  set(SAMPLE_KERNEL_SEAL_SRC main.cpp
    seal/seal_ckks_sample.cpp
    seal/seal_bfv_sample.cpp
    )

  add_executable(sample-kernels-seal ${SAMPLE_KERNEL_SEAL_SRC})
  target_link_libraries(sample-kernels-seal PRIVATE OpenMP::OpenMP_CXX)
  target_include_directories(sample-kernels-seal PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

  target_link_libraries(sample-kernels-seal PRIVATE SEAL::seal seal_kernel_executor)
  target_link_libraries(sample-kernels-seal PRIVATE libgbenchmark)
  target_link_libraries(sample-kernels-seal PRIVATE Threads::Threads)
endif()

if (${ENABLE_PALISADE})
  # PALISADE sample kernel

  # Find HEXL (optional)
  find_package(HEXL)

  # Find package Palisade and create library libpalisade
  include(../cmake/palisade.cmake)

  set(SAMPLE_KERNEL_PALISADE_SRC main.cpp
    palisade/palisade_ckks_sample.cpp
    palisade/palisade_bfv_sample.cpp
    )

  add_executable(sample-kernels-palisade ${SAMPLE_KERNEL_PALISADE_SRC})

  target_include_directories(sample-kernels-palisade PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

  target_link_libraries(sample-kernels-palisade PRIVATE libpalisade palisade_kernel_executor)
  target_link_libraries(sample-kernels-palisade PRIVATE libgbenchmark)
  target_link_libraries(sample-kernels-palisade PRIVATE Threads::Threads)

endif()

add_subdirectory(test)
add_subdirectory(kernels)
