# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(FetchContent)

FetchContent_Declare(
  gflags
  PREFIX gflags
  GIT_REPOSITORY https://github.com/gflags/gflags.git
  GIT_TAG v2.2.2
)
FetchContent_GetProperties(gflags)

if(NOT gflags_POPULATED)
  FetchContent_Populate(gflags)
  set(CMAKE_C_COMPILER ${CMAKE_C_COMPILER} CACHE STRING "" FORCE)
  set(CMAKE_CXX_COMPILER ${CMAKE_CXX_COMPILER} CACHE STRING "" FORCE)
  set(CMAKE_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX} CACHE STRING "" FORCE)

  mark_as_advanced(BUILD_gflags)
  mark_as_advanced(INSTALL_gflags)
  mark_as_advanced(FETCHCONTENT_SOURCE_DIR_gflags)
  mark_as_advanced(FETCHCONTENT_UPDATES_DISCONNECTED_gflags)

  add_subdirectory(
      ${gflags_SOURCE_DIR}
      EXCLUDE_FROM_ALL
  )
endif()
