# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set(SAMPLE_KERNELS_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR})

add_subdirectory(kernels)
add_subdirectory(test)

if (${ENABLE_SEAL})
    # SEAL sample kernel

    set(SAMPLE_KERNEL_SEAL_SRC main.cpp
	    seal/seal_ckks_sample.cpp
	    seal/seal_bfv_sample.cpp
    )

    add_executable(sample-kernels-seal ${SAMPLE_KERNEL_SEAL_SRC})

    target_include_directories(sample-kernels-seal PRIVATE ".")
    target_compile_options(sample-kernels-seal PRIVATE ${BENCHMARKS_COMPILE_FLAGS})

    target_link_libraries(sample-kernels-seal PRIVATE SEAL::seal seal_kernel_executor)
    target_link_libraries(sample-kernels-seal PRIVATE libgbenchmark)
    target_link_libraries(sample-kernels-seal PRIVATE Threads::Threads)
endif()

if (${ENABLE_PALISADE})
    # PALISADE sample kernel

    set(SAMPLE_KERNEL_PALISADE_SRC main.cpp
    	palisade/palisade_ckks_sample.cpp
	    palisade/palisade_bfv_sample.cpp
    )

    add_executable(sample-kernels-palisade ${SAMPLE_KERNEL_PALISADE_SRC})

    target_include_directories(sample-kernels-palisade PRIVATE ".")
    target_compile_options(sample-kernels-palisade PRIVATE ${BENCHMARKS_COMPILE_FLAGS})

    target_link_libraries(sample-kernels-palisade PRIVATE libpalisade palisade_kernel_executor)
    target_link_libraries(sample-kernels-palisade PRIVATE libgbenchmark)
    target_link_libraries(sample-kernels-palisade PRIVATE Threads::Threads)

endif()
