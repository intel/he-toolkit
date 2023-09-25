# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

project(encoder-source LANGUAGES CXX)

cmake_minimum_required(VERSION 3.22 FATAL_ERROR)

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

enable_testing()
add_subdirectory(tests)
