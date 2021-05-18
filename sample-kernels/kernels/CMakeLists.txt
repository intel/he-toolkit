# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# PALISADE ops
if (${ENABLE_PALISADE})
    set(PALISADE_KERNEL_EXECUTOR_SRC
        palisade/palisade_ckks_kernel_executor.cpp
        palisade/palisade_bfv_kernel_executor.cpp
        palisade/omp_utils_palisade.cpp
        )

    add_library(palisade_kernel_executor SHARED ${PALISADE_KERNEL_EXECUTOR_SRC})
    target_include_directories(palisade_kernel_executor PRIVATE ${SAMPLE_KERNELS_SRC_DIR})
    target_link_libraries(palisade_kernel_executor PRIVATE libpalisade)
endif()

# SEAL ops
if (${ENABLE_SEAL})
    set(SEAL_KERNEL_EXECUTOR_SRC
        seal/seal_ckks_kernel_executor.cpp
        seal/seal_ckks_context.cpp
        seal/seal_bfv_kernel_executor.cpp
        seal/seal_bfv_context.cpp
        seal/seal_omp_utils.cpp
        )
    add_library(seal_kernel_executor SHARED ${SEAL_KERNEL_EXECUTOR_SRC})
    target_include_directories(seal_kernel_executor PRIVATE ${SAMPLE_KERNELS_SRC_DIR})
    target_link_libraries(seal_kernel_executor PRIVATE libseal)
endif()
