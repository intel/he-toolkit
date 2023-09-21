// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>

#include "../balanced.h"

namespace {

using hekit::coder::BalancedSlotsParams;
using hekit::coder::Coder;
using hekit::coder::SparsePoly;
using vec_double = std::vector<double>;

class MultiNum : public testing::TestWithParam<std::vector<double>> {};

TEST_P(MultiNum, testCompareOriginalToDecodedEncoded) {
  BalancedSlotsParams params{.rw = 1.2, .epsil = 1e-8};
  Coder coder{params};
  const auto& original = GetParam();
  const auto& encoded = coder.encode(original);
  const auto& is = encoded.digits();
  const auto decoded = coder.decode(encoded);

  for (int i = 0; i < original.size(); ++i)
    EXPECT_NEAR(original[i], decoded[i], params.epsil)
        << "i, digit: " << i << ", " << is[i];
}

INSTANTIATE_TEST_SUITE_P(
    variousSingleNumbers, MultiNum,
    // zero, integer_part, double
    ::testing::Values(vec_double{0.0, 1.2, 0.235, 12.3, 546, 546.789},
                      vec_double{21, 2.987, 5.678},
                      vec_double{0.000000001, 12345, 2345.987}));

struct TestBalancedSlotsArith {
  double num1;
  double num2;
  double rw;
  double epsil;
};

class BalancedSlotsArith
    : public testing::TestWithParam<TestBalancedSlotsArith> {};

TEST_P(BalancedSlotsArith, testBalancedSlotsAddition) {
  auto& [num1, num2, rw, epsil] = GetParam();

  BalancedSlotsParams params{rw, epsil};
  Coder coder(params);
  const auto& encoded1 = coder.encode({num1});
  const auto& encoded2 = coder.encode({num2});
  const auto decoded = coder.decode(encoded1 + encoded2);

  EXPECT_NEAR(num1 + num2, decoded[0], epsil);
}

TEST_P(BalancedSlotsArith, testBalancedSlotsMultiplication) {
  auto& [num1, num2, rw, epsil] = GetParam();

  BalancedSlotsParams params{rw, epsil};
  Coder coder(params);
  const auto& encoded1 = coder.encode({num1});
  const auto& encoded2 = coder.encode({num2});
  const auto decoded = coder.decode(encoded1 * encoded2);

  EXPECT_NEAR(num1 * num2, decoded[0], epsil);
}

double default_epsil = 1e-8;

INSTANTIATE_TEST_SUITE_P(variousParameters, BalancedSlotsArith,
                         ::testing::Values(
                             /*integer*/
                             TestBalancedSlotsArith{234.0, 241.0, 1.2,
                                                    default_epsil}));

}  // namespace
