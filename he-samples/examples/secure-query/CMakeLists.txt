# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#####################################################################
## secure-query Binary:
#####################################################################

cmake_minimum_required(VERSION 3.13 FATAL_ERROR)

## Use -std=c++17 as default.
set(CMAKE_CXX_STANDARD 17)
## Disable C++ extensions
set(CMAKE_CXX_EXTENSIONS OFF)
## Require full C++ standard
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SECURE_QUERY_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR})
add_executable(secure-query)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if (TARGET libseal) ## true if doing online/offline he-toolkit build
        target_link_libraries(secure-query PRIVATE libseal)
else() ## true if building secure query standalone
        include_directories(${SEAL_PREFIX}/include/SEAL-3.7/)
        target_link_libraries(secure-query PUBLIC ${SEAL_PREFIX}/lib/libseal-3.7.a)
endif()

set(THREADS_PREFER_PTHREAD_FLAG ON)
target_link_libraries(secure-query PRIVATE Threads::Threads)
find_package(Threads REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp")

include_directories(
            ${SECURE_QUERY_SRC_DIR}/include
        ${SECURE_QUERY_SRC_DIR}/src
        )

file(GLOB SQ_SRCS
            "${SECURE_QUERY_SRC_DIR}/include/*.h"
        "${SECURE_QUERY_SRC_DIR}/include/*.hpp"
            "${SECURE_QUERY_SRC_DIR}/src/*.cpp"
        )
    target_sources(secure-query PUBLIC ${SQ_SRCS})

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/datasets/us_state_capitals.csv
    DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/)
