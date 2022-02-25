# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#FIXME: Need logic for setting HINT DIR
set(PALISADE_HINT_DIR ${HEKIT_DIR}/components/palisade/v1.11.6/install
  CACHE PATH "Location of PALISADE install")
message(STATUS "PALISADE_HINT_DIR: ${PALISADE_HINT_DIR}")

find_package(Palisade
  HINTS ${PALISADE_HINT_DIR}
  REQUIRED)

message(STATUS "PALISADE_INCLUDE ${PALISADE_INCLUDE}")
message(STATUS "PALISADE_LIBRARIES ${PALISADE_LIBRARIES}")
message(STATUS "PALISADE_LIBDIR ${PALISADE_LIBDIR}")
message(STATUS "OPENMP_INCLUDES ${OPENMP_INCLUDES}")
message(STATUS "OPENMP_LIBRARIES ${OPENMP_LIBRARIES}")

add_library(libpalisade INTERFACE)
target_include_directories(libpalisade INTERFACE
  ${OPENMP_INCLUDES} # Will be empty if PALISADE is built single-threaded
  ${PALISADE_INCLUDE}
  ${PALISADE_INCLUDE}/third-party/include
  ${PALISADE_INCLUDE}/core
  ${PALISADE_INCLUDE}/pke
  ${PALISADE_INCLUDE}/binfhe
  )

target_link_directories(libpalisade INTERFACE ${PALISADE_LIBDIR})
target_link_libraries(libpalisade INTERFACE ${PALISADE_LIBRARIES} ${OPENMP_LIBRARIES})

# Ignore errors from PALISADE
add_compile_options(-Wno-error=unused-parameter -Wno-error=ignored-qualifiers -Wno-error=deprecated-copy)
