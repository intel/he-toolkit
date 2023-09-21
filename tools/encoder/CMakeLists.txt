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

add_subdirectory(tests)
