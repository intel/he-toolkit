# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Defines "helib" target

include(FetchContent)

option(HELIB_PREBUILT OFF) # Set to ON/OFF to use prebuilt installation
message(STATUS "HELIB_PREBUILT: ${HELIB_PREBUILT}")

if (HELIB_PREBUILT) # Skip download from GitHub
  message(STATUS "HELIB_HINT_DIR: ${HELIB_HINT_DIR}")
  find_package(helib HINTS ${HELIB_HINT_DIR} REQUIRED)
else()
  FetchContent_Declare(
    helib
    PREFIX helib
    GIT_REPOSITORY https://github.com/homenc/HElib.git
    GIT_TAG v2.2.1
  )
  FetchContent_GetProperties(helib)

  if(NOT helib_POPULATED)
    FetchContent_Populate(helib)

    set(BUILD_SHARED OFF CACHE BOOL "" FORCE)
    set(PACKAGE_BUILD OFF CACHE BOOL "" FORCE)
    set(ENABLE_THREADS ON CACHE BOOL "" FORCE)
    set(HELIB_DEBUG OFF CACHE BOOL "" FORCE)
    set(ENABLE_TEST OFF CACHE BOOL "" FORCE)
    set(USE_INTEL_HEXL ${ENABLE_INTEL_HEXL} CACHE STRING "" FORCE)
    set(HEXL_DIR ${INTEL_HEXL_HINT_DIR} CACHE STRING "" FORCE)
    set(PEDANTIC_BUILD ON CACHE BOOL "" FORCE)

    add_subdirectory(
      ${helib_SOURCE_DIR}
      EXCLUDE_FROM_ALL
    )
  endif()
endif()
