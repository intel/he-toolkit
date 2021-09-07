# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


# linking non-global imports requires >= 3.13
cmake_minimum_required(VERSION 3.13)

project(he-benchmarks LANGUAGES C CXX)

if(CMAKE_BUILD_TYPE)
  set(RELEASE_TYPES
      Debug
      Release
      RelWithDebInfo
      MinSizeRel)
  list(FIND RELEASE_TYPES ${CMAKE_BUILD_TYPE} INDEX_FOUND)
  if(${INDEX_FOUND} EQUAL -1)
    message(
      FATAL_ERROR
        "CMAKE_BUILD_TYPE must be one of Debug, Release, RelWithDebInfo, or MinSizeRel"
      )
  endif()
endif()

# SEAL uses C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Create compilation database compile_commands.json
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Set flags to forward to external projects
set(BENCHMARK_FORWARD_CMAKE_ARGS
    -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
    -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    -DCMAKE_CXX_STANDARD=${CMAKE_CXX_STANDARD}
    -DCMAKE_CXX_STANDARD_REQUIRED=${CMAKE_CXX_STANDARD_REQUIRED}
    -DCMAKE_CXX_EXTENSIONS=${CMAKE_CXX_EXTENSIONS}
    -DCMAKE_EXPORT_COMPILE_COMMANDS=${CMAKE_EXPORT_COMPILE_COMMANDS}
    -DCMAKE_POSITION_INDEPENDENT_CODE=${CMAKE_POSITION_INDEPENDENT_CODE}
    -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
    -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
)

#------------------------------------------------------------------------------
# Options...
#------------------------------------------------------------------------------
option(ENABLE_HELIB "Enable HElib library" ON)
option(ENABLE_PALISADE "Enable PALISADE library" ON)
option(ENABLE_SEAL "Enable SEAL library" ON)
option(ENABLE_INTEL_HEXL "Enable Intel HEXL library" ON)

# Sanitizers
option(ENABLE_ADDRESS_SANITIZER "Compiles and links with Address Sanitizer" OFF)
option(ENABLE_THREAD_SANITIZER "Compiles and links with Thread Sanitizer" OFF)
option(ENABLE_UB_SANITIZER "Compiles and links with Undefined Behavior Sanitizer" OFF)

message(STATUS "ENABLE_HELIB:             ${ENABLE_HELIB}")
message(STATUS "ENABLE_PALISADE:          ${ENABLE_PALISADE}")
message(STATUS "ENABLE_SEAL:              ${ENABLE_SEAL}")
message(STATUS "ENABLE_ADDRESS_SANITIZER: ${ENABLE_ADDRESS_SANITIZER}")
message(STATUS "ENABLE_THREAD_SANITIZER:  ${ENABLE_THREAD_SANITIZER}")
message(STATUS "ENABLE_UB_SANITIZER:      ${ENABLE_UB_SANITIZER}")
message(STATUS "ENABLE_INTEL_HEXL:        ${ENABLE_INTEL_HEXL}")

#--------------------------------------------------------------------
# Compiler logic
#--------------------------------------------------------------------

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native")

set(SINGLE_THREAD_CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS})
set(SINGLE_THREAD_CMAKE_C_FLAGS ${CMAKE_C_FLAGS})

# OpenMP
# MacOS requires manual configuration
if (APPLE)
  set(OPENMP_LIBRARIES "/opt/local/lib/libomp")
  set(OPENMP_INCLUDES "/opt/local/include/libomp")

  if(CMAKE_C_COMPILER_ID MATCHES "Clang")
    set(OpenMP_C_FLAGS "-Xpreprocessor -fopenmp -lomp -Wno-unused-command-line-argument")
    set(OpenMP_C_LIB_NAMES "libomp")
    set(OpenMP_libomp_LIBRARY ${OpenMP_C_LIB_NAMES})
  endif()
  if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    set(OpenMP_CXX_FLAGS "-Xpreprocessor -fopenmp -lomp -Wno-unused-command-line-argument")
    set(OpenMP_CXX_LIB_NAMES "libomp")
    set(OpenMP_libomp_LIBRARY ${OpenMP_CXX_LIB_NAMES})
  endif()

  include_directories("${OPENMP_INCLUDES}")
  link_directories("${OPENMP_LIBRARIES}")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

find_package (OpenMP REQUIRED)

if (NOT APPLE)
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
  set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

#------------------------------------------------------------------------------
# Installation logic...
#------------------------------------------------------------------------------

if (LINUX)
    include(GNUInstallDirs)
else()
    set(CMAKE_INSTALL_BINDIR "bin")
    set(CMAKE_INSTALL_INCLUDEDIR "include")
    set(CMAKE_INSTALL_DOCDIR "doc")
    set(CMAKE_INSTALL_LIBDIR "lib")
endif()

if (NOT ${CMAKE_INSTALL_PREFIX})
  set (CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_BINARY_DIR})
endif()

message(STATUS "CMAKE_INSTALL_PREFIX ${CMAKE_INSTALL_PREFIX}")

if(ENABLE_ADDRESS_SANITIZER)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fsanitize=leak")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address -fsanitize=leak")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -fsanitize=address -fsanitize=leak")
endif()

if(ENABLE_UB_SANITIZER)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=float-divide-by-zero -fsanitize=undefined -fsanitize=float-cast-overflow -fsanitize=implicit-conversion -fPIE")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=float-divide-by-zero -fsanitize=undefined -fsanitize=float-cast-overflow -fsanitize=implicit-conversion  -fPIE -pie")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -fsanitize=float-divide-by-zero -fsanitize=undefined -fsanitize=float-cast-overflow -fsanitize=implicit-conversion -fPIE -pie")
endif()

if(ENABLE_THREAD_SANITIZER)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=thread")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=thread")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -fsanitize=thread")
endif()

if(ENABLE_ADDRESS_SANITIZER OR ENABLE_THREAD_SANITIZER OR ENABLE_UB_SANITIZER)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -fno-omit-frame-pointer")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -g -fno-omit-frame-pointer")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -g -fno-omit-frame-pointer")
endif()



#------------------------------------------------------------------------------
# Third-party code...
#------------------------------------------------------------------------------
# Pthreads
# Assume pthreads are built-in on macOS
if(APPLE)
  set(CMAKE_THREAD_LIBS_INIT "-lpthread")
  set(CMAKE_HAVE_THREADS_LIBRARY 1)
  set(CMAKE_USE_WIN32_THREADS_INIT 0)
  set(CMAKE_USE_PTHREADS_INIT 1)
endif()
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

if (${ENABLE_SEAL})
  include(cmake/seal.cmake)
endif()

if (${ENABLE_PALISADE})
  include(cmake/palisade.cmake)
endif()

if (${ENABLE_HELIB})
  include(cmake/helib.cmake)
endif()

include(cmake/gtest.cmake)
include(cmake/gbenchmark.cmake)
include(cmake/gflags.cmake)
#------------------------------------------------------------------------------
# Subfolders...
#------------------------------------------------------------------------------

set(SRC_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

if(POCBENCH_DIR)
  get_filename_component(POCBENCH_DIR_FULLPATH "${POCBENCH_DIR}" REALPATH)

  if(IS_DIRECTORY ${POCBENCH_DIR_FULLPATH})
    if(EXISTS "${POCBENCH_DIR_FULLPATH}/CMakeLists.txt")
      message(STATUS "Adding ${POCBENCH_DIR_FULLPATH} for POCBENCH")
      add_subdirectory(${POCBENCH_DIR_FULLPATH} "${CMAKE_CURRENT_BINARY_DIR}/pocbench")
    endif()
  endif()
endif()

add_subdirectory(sample-kernels)
add_subdirectory(examples)
