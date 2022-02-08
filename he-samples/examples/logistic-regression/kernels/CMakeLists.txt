# Copyright (C) 2020 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Logistic Regression HE Kernel ops
set(LRHE_KERNEL_SRC
    lrhe_kernel.cpp
    omp_utils.cpp
)

add_library(lrhe_kernel SHARED ${LRHE_KERNEL_SRC})
target_include_directories(lrhe_kernel PRIVATE ${LR_BENCH_SRC_DIR})
target_link_libraries(lrhe_kernel PRIVATE libseal)
