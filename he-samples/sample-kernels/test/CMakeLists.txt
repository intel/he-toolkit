# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set(SRC main.cpp)

if (${ENABLE_PALISADE})
    set(SRC ${SRC}
        test_palisade.cpp
        test_palisade_ckks_kernel_executor.cpp
        test_palisade_bfv_kernel_executor.cpp
        )
endif()

if (${ENABLE_SEAL})
    set(SRC ${SRC}
        test_seal.cpp
        test_seal_ckks_kernel_executor.cpp
        test_seal_bfv_kernel_executor.cpp
        )
endif()

add_executable(unit-test ${SRC})

target_include_directories(unit-test PRIVATE ".")
target_include_directories(unit-test PRIVATE ${SAMPLE_KERNELS_SRC_DIR})

target_link_libraries(unit-test PRIVATE libgtest)

if (${ENABLE_PALISADE})
    target_link_libraries(unit-test PRIVATE libpalisade palisade_kernel_executor)
endif()

if (${ENABLE_SEAL})
    target_link_libraries(unit-test PRIVATE libseal seal_kernel_executor)
endif()

target_link_libraries(unit-test PRIVATE Threads::Threads)
