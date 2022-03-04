# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(ExternalProject)

# If user has not specified an install path, override the default usr/local to
# be the build directory of the original target.
if (NOT ${CMAKE_INSTALL_PREFIX})
  set (CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_BINARY_DIR})
endif()

set(GBENCHMARK_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/ext_gbenchmark)

set(GBENCHMARK_SRC_DIR ${GBENCHMARK_PREFIX}/src/ext_gbenchmark/)
set(GBENCHMARK_BUILD_DIR ${GBENCHMARK_PREFIX}/src/ext_gbenchmark-build/)
set(GBENCHMARK_REPO_URL https://github.com/google/benchmark.git)
set(GBENCHMARK_GIT_TAG v1.5.6)

set(GBENCHMARK_PATHS ${GBENCHMARK_SRC_DIR} ${GBENCHMARK_BUILD_DIR}/src/libbenchmark.a)

ExternalProject_Add(
  ext_gbenchmark
  GIT_REPOSITORY ${GBENCHMARK_REPO_URL}
  GIT_TAG ${GBENCHMARK_GIT_TAG}
  PREFIX  ${GBENCHMARK_PREFIX}
  CMAKE_ARGS ${BENCHMARK_FORWARD_CMAKE_ARGS}
             -DCMAKE_INSTALL_LIBDIR=${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}
             -DCMAKE_INSTALL_INCLUDEDIR=${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_INCLUDEDIR}
             -DBENCHMARK_ENABLE_GTEST_TESTS=OFF
             -DBENCHMARK_ENABLE_TESTING=OFF
             -DCMAKE_BUILD_TYPE=Release
  BUILD_BYPRODUCTS ${GBENCHMARK_PATHS}
  # Skip updates
  UPDATE_COMMAND ""
)

add_library(libgbenchmark INTERFACE)
add_dependencies(libgbenchmark ext_gbenchmark)

ExternalProject_Get_Property(ext_gbenchmark SOURCE_DIR BINARY_DIR)

target_link_libraries(libgbenchmark INTERFACE ${GBENCHMARK_BUILD_DIR}/src/libbenchmark.a)

target_include_directories(libgbenchmark SYSTEM
                                    INTERFACE ${GBENCHMARK_SRC_DIR}/include)
