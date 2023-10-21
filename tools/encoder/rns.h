// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <algorithm>
#include <numeric>
#include <tuple>
#include <utility>

namespace hekit::coder {

// https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
struct ExtendedEuclidResults {
  long gcd;
  long a;
  long b;
};

inline auto extendedGCD(long a, long b) -> ExtendedEuclidResults {
  if (b == 0) return ExtendedEuclidResults{.gcd = a, .a = 1, .b = 0};

  auto [old_r, r] = std::pair{a, b};
  auto [old_s, s] = std::pair{1L, 0L};
  auto [old_t, t] = std::pair{0L, 1L};

  while (r != 0) {
    auto quotient = old_r / r;
    std::tie(old_r, r) = std::make_tuple(r, old_r - quotient * r);
    std::tie(old_s, s) = std::make_tuple(s, old_s - quotient * s);
    std::tie(old_t, t) = std::make_tuple(t, old_t - quotient * t);
  }

  return ExtendedEuclidResults{.gcd = std::abs(old_r),
                               .a = (a < 0 ? -1 : 1) * old_s,
                               .b = (b < 0 ? -1 : 1) * old_t};
}

inline long solveCRT(std::pair<long, long> am, std::pair<long, long> bn) {
  const auto result = extendedGCD(am.second, bn.second);
  if (result.gcd != 1) throw std::runtime_error("");
  const auto recompose =
      am.first * bn.second * result.b + bn.first * am.second * result.a;
  return recompose % (bn.second * am.second);
}

}  // namespace hekit::coder
