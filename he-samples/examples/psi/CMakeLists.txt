# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#####################################################################
## Private Set Intersection (PSI)
#####################################################################

cmake_minimum_required(VERSION 3.10.2 FATAL_ERROR)

## Use -std=c++17 as default.
set(CMAKE_CXX_STANDARD 17)
## Disable C++ extensions
set(CMAKE_CXX_EXTENSIONS OFF)
## Require full C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)

project(psi LANGUAGES CXX)
find_package(helib 2.2.0 REQUIRED)
add_executable(psi psi.cpp)
target_link_libraries(psi helib)
