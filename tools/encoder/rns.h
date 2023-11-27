// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <algorithm>
#include <numeric>
#include <tuple>
#include <utility>
#include <NTL/RR.h>

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

inline auto decompCRT(long num, const std::pair<long, long>& mod_pair)
    -> std::pair<long, long> {
  return std::pair{num % mod_pair.first, num % mod_pair.second};
}

// TODO Write with NTL?
using ZZ_pair = std::pair<NTL::ZZ, NTL::ZZ>;
inline NTL::ZZ recompCRT(const ZZ_pair& am, const ZZ_pair& bn) {
  // TODO use NTL version or rewrite this one
  NTL::ZZ gcd, a, b;
  NTL::XGCD(gcd, a, b, am.second, bn.second);
  if (gcd != 1L) throw std::runtime_error("Not co-prime numbers");
  const auto big_mod = am.second * bn.second;
  const auto recompose = am.first * bn.second * b + bn.first * am.second * a;
  return recompose % big_mod;
}

// NOTE simpler impl. limited by machine word size
inline long recompCRT(const std::pair<long, long>& am,
                      const std::pair<long, long>& bn) {
  const auto result = extendedGCD(am.second, bn.second);
  if (result.gcd != 1) throw std::runtime_error("Not co-prime numbers");
  const auto big_mod = am.second * bn.second;
  const auto recompose =
      am.first * bn.second * result.b + bn.first * am.second * result.a;
  const auto recomp_mod = recompose % big_mod;
  return recomp_mod;
}

}  // namespace hekit::coder
