// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include "../euclid.h"

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

}  // namespace
