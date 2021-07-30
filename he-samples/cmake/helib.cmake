# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(ExternalProject)

option(HELIB_PREBUILT OFF) # Set to ON/OFF to use prebuilt installation
message(STATUS "HELIB_PREBUILT: ${HELIB_PREBUILT}")

if (HELIB_PREBUILT) # Skip download from GitHub
  find_package(helib 2.1.0 HINTS ${HELIB_HINT_DIR} REQUIRED)
  add_library(libhelib ALIAS helib)
else()
  set(HELIB_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/ext_helib)
  set(HELIB_SRC_DIR ${HELIB_PREFIX}/src/ext_helib/)
  set(HELIB_REPO_URL https://github.com/homenc/HElib.git)
  set(HELIB_GIT_TAG v2.1.0)

  set(HELIB_CXX_FLAGS "${CMAKE_C_FLAGS} -fvisibility=hidden -fvisibility-inlines-hidden")

  set(HELIB_SHARED_LIB OFF)

  ExternalProject_Add(
    ext_helib
    GIT_REPOSITORY ${HELIB_REPO_URL}
    GIT_TAG ${HELIB_GIT_TAG}
    PREFIX ${HELIB_PREFIX}
    INSTALL_DIR ${HELIB_PREFIX}
    CMAKE_ARGS ${BENCHMARK_FORWARD_CMAKE_ARGS}
    -DCMAKE_CXX_FLAGS=${HELIB_CXX_FLAGS}
    -DCMAKE_INSTALL_PREFIX=${HELIB_PREFIX}
    -DCMAKE_INSTALL_LIBDIR=${HELIB_PREFIX}/lib
    -DCMAKE_INSTALL_INCLUDEDIR=${HELIB_PREFIX}/include
    -DUSE_INTEL_HEXL=${ENABLE_INTEL_HEXL}
    -DBUILD_SHARED=${HELIB_SHARED_LIB}
    # Skip updates
    UPDATE_COMMAND ""
    )

  ExternalProject_Get_Property(ext_helib SOURCE_DIR BINARY_DIR)

  add_library(libhelib INTERFACE)
  add_dependencies(libhelib ext_helib)
  target_include_directories(libhelib INTERFACE ${HELIB_PREFIX}/include/helib)

  if (HELIB_SHARED_LIB)
    target_link_libraries(libhelib INTERFACE ${HELIB_PREFIX}/lib/libhelib.so)
  else()
    target_link_libraries(libhelib INTERFACE ${HELIB_PREFIX}/lib/libhelib.a)
  endif()

endif()
