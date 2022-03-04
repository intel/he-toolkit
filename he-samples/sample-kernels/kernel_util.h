// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <benchmark/benchmark.h>

#include <vector>

namespace intel {
namespace he {

#define ADD_SAMPLE_HE_ARGS Args({8192, 3})

// Generates a vector of type T with size slots small entries
template <typename T>
inline std::vector<T> generateVector(size_t slots, size_t row_size = 0,
                                     size_t n_rows = 2, size_t n_slots = 4) {
  std::vector<T> input(slots, static_cast<T>(0));
  if (row_size == 0) {
    for (size_t i = 0; i < slots; ++i) {
      input[i] = static_cast<T>(i);
    }
  } else {
    for (size_t r = 0; r < n_rows; ++r) {
      for (size_t i = 0; i < n_slots; ++i) {
        input[i + r * row_size] = static_cast<T>(i + r * n_slots);
      }
    }
  }
  return input;
}
}  // namespace he
}  // namespace intel
