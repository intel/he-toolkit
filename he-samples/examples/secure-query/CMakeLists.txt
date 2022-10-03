# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#####################################################################
## Secure Query Binary:
#####################################################################

project(secure-query LANGUAGES CXX)

cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

## Use -std=c++17 as default.
set(CMAKE_CXX_STANDARD 17)
## Disable C++ extensions
set(CMAKE_CXX_EXTENSIONS OFF)
## Require full C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(SEAL REQUIRED)

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

find_package (OpenMP REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")

file(GLOB CODE_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")
add_executable(secure-query ${CODE_SRCS})

target_link_libraries(secure-query PRIVATE OpenMP::OpenMP_CXX)
target_include_directories(secure-query PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)

target_link_libraries(secure-query PRIVATE SEAL::seal)
target_link_libraries(secure-query PRIVATE Threads::Threads)

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/datasets/us_state_capitals.csv
  DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/)
