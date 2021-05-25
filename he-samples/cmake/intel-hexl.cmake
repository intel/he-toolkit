# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(ExternalProject)

set(INTEL_HEXL_GIT_REPO_URL https://github.com/intel/hexl.git)
set(INTEL_HEXL_GIT_LABEL v1.1.0)

ExternalProject_Add(
    ext_intel_hexl
    PREFIX ext_intel_hexl
    GIT_REPOSITORY ${INTEL_HEXL_GIT_REPO_URL}
    GIT_TAG ${INTEL_HEXL_GIT_LABEL}
    CMAKE_ARGS
        -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
        -DHEXL_DEBUG=OFF
        -DHEXL_SHARED_LIB=OFF
        -DHEXL_BENCHMARK=OFF
        -DHEXL_COVERAGE=OFF
        -DHEXL_TESTING=ON
        -DHEXL_EXPORT=ON
        -DCMAKE_INSTALL_PREFIX=${CMAKE_CURRENT_BINARY_DIR}/ext_intel_hexl/
    EXCLUDE_FROM_ALL TRUE
    # Skip updates
    UPDATE_COMMAND "")

ExternalProject_Get_Property(ext_intel_hexl SOURCE_DIR BINARY_DIR)

set(INTEL_HEXL_HINT_DIR ${CMAKE_CURRENT_BINARY_DIR}/ext_intel_hexl/lib/cmake)
