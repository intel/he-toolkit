# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(ExternalProject)

option(HELIB_PREBUILT OFF) # Set to ON/OFF to use prebuilt installation
message(STATUS "HELIB_PREBUILT: ${HELIB_PREBUILT}")

if (HELIB_PREBUILT) # Skip download from GitHub

  message(STATUS "HELIB_HINT_DIR: ${HELIB_HINT_DIR}")
  find_package(helib
    HINTS ${HELIB_HINT_DIR}
    REQUIRED)

  add_library(libhelib ALIAS helib)

else()

  set(HELIB_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/ext_helib)
  set(HELIB_SRC_DIR ${HELIB_PREFIX}/src/ext_helib/)
  set(HELIB_REPO_URL https://github.com/homenc/HElib.git)
  set(HELIB_GIT_TAG v2.2.1)

  set(HELIB_CXX_FLAGS "${CMAKE_C_FLAGS} -fvisibility=hidden -fvisibility-inlines-hidden")

  set(HELIB_SHARED_LIB OFF)

  if(ENABLE_INTEL_HEXL)
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
      -DBUILD_SHARED=${HELIB_SHARED_LIB}
      -DPACKAGE_BUILD=OFF
      -DENABLE_THREADS=ON
      -DHELIB_DEBUG=OFF
      -DENABLE_TEST=OFF
      -DNTL_DIR=${NTL_DIR}
      -DGMP_DIR=${GMP_DIR}
      -DUSE_INTEL_HEXL=${ENABLE_INTEL_HEXL}
      -DHEXL_DIR=${INTEL_HEXL_HINT_DIR}
      -DPEDANTIC_BUILD=ON
      # Skip updates
      UPDATE_COMMAND ""
      )
  else(ENABLE_INTEL_HEXL)
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
      -DBUILD_SHARED=${HELIB_SHARED_LIB}
      -DPACKAGE_BUILD=OFF
      -DENABLE_THREADS=ON
      -DHELIB_DEBUG=OFF
      -DENABLE_TEST=OFF
      -DNTL_DIR=${NTL_DIR}
      -DGMP_DIR=${GMP_DIR}
      -DUSE_INTEL_HEXL=OFF
      -DPEDANTIC_BUILD=ON
      # Skip updates
      UPDATE_COMMAND ""
      )
  endif()

  ExternalProject_Get_Property(ext_helib SOURCE_DIR BINARY_DIR)

  add_library(libhelib INTERFACE)
  add_dependencies(libhelib ext_helib)
  target_include_directories(libhelib INTERFACE ${HELIB_PREFIX}/include/)

  if (HELIB_SHARED_LIB)
    target_link_libraries(libhelib INTERFACE ${HELIB_PREFIX}/lib/libhelib.so ${NTL_DIR}libntl.so ${GMP_DIR}libgmp.so)
  else()
    target_link_libraries(libhelib INTERFACE ${HELIB_PREFIX}/lib/libhelib.a ${NTL_DIR}libntl.a ${GMP_DIR}libgmp.so)
  endif()

endif()
