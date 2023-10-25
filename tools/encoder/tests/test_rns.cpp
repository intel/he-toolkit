// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include "../rns.h"

namespace {

using hekit::coder::extendedGCD;

struct TestExtendedEuclid
    : public testing::TestWithParam<std::pair<long, long>> {};

TEST_P(TestExtendedEuclid, test) {
  const auto [x, y] = GetParam();
  const auto [value, a, b] = extendedGCD(x, y);
  EXPECT_EQ(value, std::gcd(x, y)) << "x: " << x << ", y: " << y;
  EXPECT_EQ(a * x + b * y, std::gcd(x, y)) << "a: " << a << ", b: " << b;
}

INSTANTIATE_TEST_SUITE_P(
    variousNumbers, TestExtendedEuclid,
    ::testing::Values(std::pair{45L, 5L}, std::pair{5L, 45L}, std::pair{0L, 5L},
                      std::pair{7L, 0L}, std::pair{127L, 257L},
                      std::pair{-5, 45}, std::pair{-45, -5},
                      std::pair{0L, -5L}));

TEST(testRNS, DecompRecomp) {
  long original = 5432;
  long mod_a = 257;
  long mod_b = 127;

  const auto decomposed = hekit::coder::decompCRT(original, {mod_a, mod_b});

  EXPECT_LT(decomposed.first, mod_a);
  EXPECT_LT(decomposed.second, mod_b);

  const auto recomposed = hekit::coder::recompCRT({decomposed.first, mod_a},
                                                  {decomposed.second, mod_b});
  // Don't forget to mod. Easiest way to check correct.
  long big_mod = mod_a * mod_b;
  EXPECT_EQ((recomposed + big_mod) % big_mod, original);
}

}  // namespace
