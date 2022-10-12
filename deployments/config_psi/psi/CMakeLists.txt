# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#####################################################################
## Configurable Private Set Intersection (PSI) Engine
#####################################################################

project(psi LANGUAGES CXX)

cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

## Use -std=c++17 as default.
set(CMAKE_CXX_STANDARD 17)
## Disable C++ extensions
set(CMAKE_CXX_EXTENSIONS OFF)
## Require full C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Define standard installation directories (GNU)
include(GNUInstallDirs)

# Set default output folder
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY
    "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY
    "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_LIBDIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY
    "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}")

option(ENABLE_TESTS "Enable GTests" OFF)

find_package(helib REQUIRED)

set(UTILS_DIR "${helib_DIR}/../../../../fetch/HElib/utils/common")
set(PSI_DIR "${helib_DIR}/../../../../fetch/HElib/misc/psi/io")

add_executable(psi ${CMAKE_CURRENT_SOURCE_DIR}/src/configurable_psi.cpp)

target_include_directories(psi PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include ${UTILS_DIR} ${PSI_DIR} ${JSON_DIR})

target_link_libraries(psi helib)

if (ENABLE_TESTS)
  add_subdirectory(tests)
endif()
