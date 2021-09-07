// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "include/timer.hpp"

namespace intel {
namespace timer {
std::chrono::steady_clock::time_point now() {
  return std::chrono::high_resolution_clock::now();
}

double delta(std::chrono::steady_clock::time_point start) {
  auto end = now();
  return delta(start, end);
}

double delta(std::chrono::steady_clock::time_point start,
             std::chrono::steady_clock::time_point end) {
  return static_cast<double>(
             std::chrono::duration_cast<std::chrono::milliseconds>(end - start)
                 .count()) /
         1000.0;
}
}  // namespace timer
}  // namespace intel
