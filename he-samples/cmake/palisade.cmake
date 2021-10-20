# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(FetchContent)

option(PALISADE_PREBUILT OFF) # Set to ON/OFF to use prebuilt installation
message(STATUS "PALISADE_PREBUILT: ${PALISADE_PREBUILT}")

if (PALISADE_PREBUILT) # Skip download from gitlab
  message(STATUS "PALISADE_HINT_DIR: ${PALISADE_HINT_DIR}")
  find_package(Palisade HINTS ${PALISADE_HINT_DIR} REQUIRED)

  if (${ENABLE_INTEL_HEXL})
    find_package(HEXL ${HEXL_HINT_DIR} REQUIRED)
  endif()

  set(PALISADE_INCLUDE_DIR_FIX
    "${PALISADE_INCLUDE};${PALISADE_INCLUDE}/core;${PALISADE_INCLUDE}/pke;${PALISADE_INCLUDE}/binfhe"
    )

  message("PALISADE_INCLUDE_DIR_FIX ${PALISADE_INCLUDE_DIR_FIX}")

  set_target_properties(PALISADEcore PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES ${PALISADE_INCLUDE_DIR_FIX}
    INCLUDE_DIRECTORIES ${PALISADE_INCLUDE_DIR_FIX}
    )
  set_property(TARGET PALISADEcore PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${PALISADE_INCLUDE_DIR_FIX})
  set_property(TARGET PALISADEcore PROPERTY INCLUDE_DIRECTORIES ${PALISADE_INCLUDE_DIR_FIX})

else()
  FetchContent_Declare(
    palisade
    PREFIX palisade
    GIT_REPOSITORY https://gitlab.com/palisade/palisade-release.git
    GIT_TAG v1.11.5
  )
  FetchContent_GetProperties(palisade)

  if(NOT palisade_POPULATED)
    FetchContent_Populate(palisade)

    set(BUILD_UNITTESTS OFF CACHE BOOL "" FORCE)
    set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(BUILD_BENCHMARKS ON CACHE BOOL "" FORCE)
    set(BUILD_EXTRAS OFF CACHE BOOL "" FORCE)
    set(BUILD_STATIC OFF CACHE BOOL "" FORCE)
    set(WITH_BE2 ON CACHE BOOL "" FORCE)
    set(WITH_BE4 OFF CACHE BOOL "" FORCE)
    set(WITH_TCM OFF CACHE BOOL "" FORCE)
    set(WITH_OPENMP OFF CACHE BOOL "" FORCE)
    set(WITH_NATIVEOPT ON CACHE BOOL "" FORCE)
    set(WITH_INTEL_HEXL ${ENABLE_INTEL_HEXL} CACHE BOOL "" FORCE)
    set(INTEL_HEXL_PREBUILT OFF CACHE BOOL "" FORCE)
    set(INTEL_HEXL_HINT_DIR ${INTEL_HEXL_HINT_DIR})

    add_subdirectory(
      ${palisade_SOURCE_DIR}
      EXCLUDE_FROM_ALL
    )
  endif()
endif()
