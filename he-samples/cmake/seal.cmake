# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(FetchContent)

option(SEAL_PREBUILT OFF) # Set to ON/OFF to use prebuilt installation
message(STATUS "SEAL_PREBUILT: ${SEAL_PREBUILT}")

if (SEAL_PREBUILT) # Skip download from github
  find_package(SEAL 3.7 HINTS ${SEAL_HINT_DIR} REQUIRED)
else()
  FetchContent_Declare(
    seal
    PREFIX seal
    GIT_REPOSITORY https://github.com/microsoft/SEAL.git
    GIT_TAG v3.7.1
  )
  FetchContent_GetProperties(seal)

  if(NOT seal_POPULATED)
    FetchContent_Populate(seal)
    set(CMAKE_C_COMPILER ${CMAKE_C_COMPILER} CACHE STRING "" FORCE)
    set(CMAKE_CXX_COMPILER ${CMAKE_CXX_COMPILER} CACHE STRING "" FORCE)
    set(CMAKE_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX} CACHE STRING "" FORCE)
    set(SEAL_SHARED_LIB OFF CACHE BOOL "" FORCE)
    set(SEAL_USE_CXX17 ON CACHE BOOL "" FORCE)
    set(SEAL_USE_INTEL_HEXL ${ENABLE_INTEL_HEXL})

    add_subdirectory(
        ${seal_SOURCE_DIR}
        EXCLUDE_FROM_ALL
    )
  endif()
endif()
