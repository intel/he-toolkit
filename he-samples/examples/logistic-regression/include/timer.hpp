// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_UTILS_HPP_
#define HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_UTILS_HPP_

#pragma once

#include <sys/stat.h>
#include <unistd.h>

#include <chrono>

namespace intel {

namespace timer {
// Get current time with chrono::high_resolution_clock
std::chrono::steady_clock::time_point now();

// Get delta time since start to end in seconds
double delta(std::chrono::steady_clock::time_point start,
             std::chrono::steady_clock::time_point end);

// Get delta time since start in seconds
double delta(std::chrono::steady_clock::time_point start);

}  // namespace timer
}  // namespace intel
#endif  // HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_UTILS_HPP_
