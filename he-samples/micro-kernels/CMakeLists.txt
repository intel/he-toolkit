# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#------------------------------------------------------------------------------
# PALISADE micro-kernels
#------------------------------------------------------------------------------
if (${ENABLE_PALISADE})
    set(MICRO_SRC main.cpp
        palisade/palisade_bfv_micro.cpp
        palisade/palisade_bfvB_micro.cpp
        palisade/palisade_ckks_micro.cpp
        palisade/palisade_micro.cpp
    )

    add_executable(micro-kernels-palisade ${MICRO_SRC})

    target_include_directories(micro-kernels-palisade PRIVATE ".")
    target_compile_options(micro-kernels-palisade PRIVATE ${BENCHMARKS_COMPILE_FLAGS})

    target_link_libraries(micro-kernels-palisade PRIVATE libgbenchmark)
    target_link_libraries(micro-kernels-palisade PRIVATE libpalisade)
    target_link_libraries(micro-kernels-palisade PRIVATE Threads::Threads)
endif()

if (${ENABLE_SEAL})
    #------------------------------------------------------------------------------
    # SEAL micro-kernels
    #------------------------------------------------------------------------------

    set(MICRO_SRC main.cpp
            seal/seal_ckks_micro.cpp
            seal/seal_bfv_micro.cpp
            seal/seal_micro.cpp
            seal/seal_bfv_context.cpp
            seal/seal_ckks_context.cpp
    )

    add_executable(micro-kernels-seal ${MICRO_SRC})
    target_include_directories(micro-kernels-seal PRIVATE ".")
    target_compile_options(micro-kernels-seal PRIVATE ${BENCHMARKS_COMPILE_FLAGS})

    target_link_libraries(micro-kernels-seal PRIVATE libgbenchmark)
    target_link_libraries(micro-kernels-seal PRIVATE libseal)
    target_link_libraries(micro-kernels-seal PRIVATE Threads::Threads)
endif()
