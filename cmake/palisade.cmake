# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

include(ExternalProject)

option(PALISADE_PREBUILT OFF) # Set to ON/OFF to use prebuilt installation
message(STATUS "PALISADE_PREBUILT: ${PALISADE_PREBUILT}")

if (PALISADE_PREBUILT) # Skip download from gitlab

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
    ${PALISADE_INCLUDE}/signature
    ${PALISADE_INCLUDE}/binfhe
    ${PALISADE_INCLUDE}/abe
    )

  target_link_directories(libpalisade INTERFACE ${PALISADE_LIBDIR})
  target_link_libraries(libpalisade INTERFACE ${PALISADE_LIBRARIES} ${OPENMP_LIBRARIES})

  # Ignore errors from PALISADE
  add_compile_options(-Wno-error=unused-parameter -Wno-error=ignored-qualifiers -Wno-error=deprecated-copy)

else()

  set(PALISADE_PREFIX ${CMAKE_CURRENT_BINARY_DIR}/ext_palisade)
  set(PALISADE_SRC_DIR ${PALISADE_PREFIX}/src/ext_palisade/)
  set(PALISADE_REPO_URL https://gitlab.com/palisade/palisade-development.git)
  set(PALISADE_GIT_TAG 28f933e9)

  if (ENABLE_INTEL_HEXL)
    ExternalProject_Add(
      ext_palisade
      GIT_REPOSITORY ${PALISADE_REPO_URL}
      GIT_TAG ${PALISADE_GIT_TAG}
      PREFIX ${PALISADE_PREFIX}
      CMAKE_ARGS
      -DCMAKE_INSTALL_PREFIX=${PALISADE_PREFIX}
      -DCMAKE_CXX_FLAGS=${SINGLE_THREAD_CMAKE_CXX_FLAGS}
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
      -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
      -DCMAKE_INSTALL_LIBDIR=${PALISADE_PREFIX}/${CMAKE_INSTALL_LIBDIR}
      -DCMAKE_INSTALL_INCLUDEDIR=${PALISADE_PREFIX}/${CMAKE_INSTALL_INCLUDEDIR}
      -DBUILD_UNITTESTS=OFF
      -DBUILD_EXAMPLES=OFF
      -DBUILD_BENCHMARKS=ON
      -DBUILD_EXTRAS=OFF
      -DBUILD_STATIC=OFF
      -DWITH_BE2=ON
      -DWITH_BE4=OFF
      -DWITH_TCM=OFF
      -DWITH_OPENMP=OFF
      -DWITH_NATIVEOPT=ON
      -DWITH_INTEL_HEXL=${ENABLE_INTEL_HEXL}
      -DINTEL_HEXL_PREBUILT=OFF
      -DINTEL_HEXL_HINT_DIR=${INTEL_HEXL_HINT_DIR}
      BUILD_COMMAND $(MAKE) -j all
      # Skip updates
      UPDATE_COMMAND ""
      DEPENDS ext_intel_hexl
    )
  else()
    ExternalProject_Add(
      ext_palisade
      GIT_REPOSITORY ${PALISADE_REPO_URL}
      GIT_TAG ${PALISADE_GIT_TAG}
      PREFIX ${PALISADE_PREFIX}
      CMAKE_ARGS
      -DCMAKE_INSTALL_PREFIX=${PALISADE_PREFIX}
      -DCMAKE_CXX_FLAGS=${SINGLE_THREAD_CMAKE_CXX_FLAGS}
      -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
      -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
      -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
      -DCMAKE_INSTALL_LIBDIR=${PALISADE_PREFIX}/${CMAKE_INSTALL_LIBDIR}
      -DCMAKE_INSTALL_INCLUDEDIR=${PALISADE_PREFIX}/${CMAKE_INSTALL_INCLUDEDIR}
      -DBUILD_UNITTESTS=OFF
      -DBUILD_EXAMPLES=OFF
      -DBUILD_BENCHMARKS=ON
      -DBUILD_EXTRAS=OFF
      -DBUILD_STATIC=OFF
      -DWITH_BE2=ON
      -DWITH_BE4=OFF
      -DWITH_TCM=OFF
      -DWITH_OPENMP=OFF
      -DWITH_NATIVEOPT=ON
      -DWITH_INTEL_HEXL=OFF
      BUILD_COMMAND $(MAKE) -j all
      # Skip updates
      UPDATE_COMMAND ""
    )
  endif()

  ExternalProject_Get_Property(ext_palisade SOURCE_DIR BINARY_DIR)

  # PALISADE core
  add_library(libpalisade_core INTERFACE)
  add_dependencies(libpalisade_core ext_palisade)
  target_include_directories(libpalisade_core SYSTEM
                            INTERFACE ${PALISADE_SRC_DIR}/src/core/include)
  target_include_directories(libpalisade_core SYSTEM
                            INTERFACE ${BINARY_DIR}/src/core)
  target_include_directories(libpalisade_core SYSTEM
                            INTERFACE ${SOURCE_DIR}/third-party/cereal/include)
  target_link_libraries(libpalisade_core
                        INTERFACE ${BINARY_DIR}/lib/libPALISADEcore.so)

  # PALISADE binfhe
  # add_library(libpalisade_binfhe INTERFACE)
  # add_dependencies(libpalisade_binfhe ext_palisade)
  # target_include_directories(libpalisade_binfhe SYSTEM
  #                           INTERFACE ${PALISADE_SRC_DIR}/src/binfhe/include)
  # target_include_directories(libpalisade_binfhe SYSTEM
  #                           INTERFACE ${SOURCE_DIR}/third-party/cereal/include)
  # target_link_libraries(libpalisade_binfhe
  #                       INTERFACE ${BINARY_DIR}/lib/libPALISADEbinfhe.so)

  # PALISADE pke
  add_library(libpalisade_pke INTERFACE)
  add_dependencies(libpalisade_pke ext_palisade libpalisade_core)

  target_include_directories(libpalisade_pke SYSTEM
                            INTERFACE ${PALISADE_SRC_DIR}/src/pke/include)
  target_link_libraries(libpalisade_pke INTERFACE libpalisade_core)
  target_link_libraries(libpalisade_pke
                        INTERFACE ${BINARY_DIR}/lib/libPALISADEpke.so)

  # Create interface to multiple PALISADE libraries to be consistent with PALISADE_PREBUILT=ON
  add_library(libpalisade INTERFACE)
  target_link_libraries(libpalisade INTERFACE
    libpalisade_core  libpalisade_pke
    # libpalisade_binfhe
    )

endif()
