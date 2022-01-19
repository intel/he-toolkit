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

add_executable(psi psi.cpp)

if (TARGET libhelib) # Check if HElib has been built by the toolkit
  target_link_libraries(psi PUBLIC libhelib)
else()
  find_package(helib HINTS ${HELIB_PREFIX}/share/cmake/helib/ REQUIRED)
  target_link_libraries(psi PRIVATE helib)
endif()

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/datasets/
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/)
