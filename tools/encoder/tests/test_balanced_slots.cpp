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
  double rw;
  double epsil;
  std::vector<double> nums1;
  std::vector<double> nums2;
};

class BalancedSlotsArith
    : public testing::TestWithParam<TestBalancedSlotsArith> {};

TEST_P(BalancedSlotsArith, testBalancedSlotsAddition) {
  const auto& [rw, epsil, nums1, nums2] = GetParam();

  BalancedSlotsParams params{rw, epsil};
  Coder coder(params);
  const auto& encoded1 = coder.encode(nums1);
  const auto& encoded2 = coder.encode(nums2);
  const auto decoded = coder.decode(encoded1 + encoded2);

  ASSERT_EQ(nums1.size(), nums2.size());
  for (long n = 0; n < nums1.size(); ++n) {
    const auto& num1 = nums1[n];
    const auto& num2 = nums2[n];
    EXPECT_NEAR(num1 + num2, decoded[n], epsil) << num1 << " + " << num2;
  }
}

TEST_P(BalancedSlotsArith, testBalancedSlotsMultiplication) {
  const auto& [rw, epsil, nums1, nums2] = GetParam();

  BalancedSlotsParams params{rw, epsil};
  Coder coder(params);
  const auto& encoded1 = coder.encode(nums1);
  const auto& encoded2 = coder.encode(nums2);
  const auto decoded = coder.decode(encoded1 * encoded2);

  ASSERT_EQ(nums1.size(), nums2.size());
  for (long n = 0; n < nums1.size(); ++n) {
    const auto& num1 = nums1[n];
    const auto& num2 = nums2[n];
    // (X + espil)*(Y + epsil) = XY + epsil*(X+Y) + espil^2. epsil^2 is negl.
    const auto error = epsil * (num1 + num2);
    EXPECT_NEAR(num1 * num2, decoded[n], error) << num1 << " * " << num2;
  }
}

TEST_P(BalancedSlotsArith, testBalancedSlotsNegate) {
  const auto& [rw, epsil, nums, _] = GetParam();

  BalancedSlotsParams params{rw, epsil};
  Coder coder(params);
  auto encoded = coder.encode(nums);
  encoded.negate();
  const auto decoded = coder.decode(encoded);

  for (long n = 0; n < nums.size(); ++n) {
    const auto& num = nums[n];
    EXPECT_NEAR(-num, decoded[n], epsil);
  }
}

double default_epsil = 1e-8;

INSTANTIATE_TEST_SUITE_P(
    variousParameters, BalancedSlotsArith,
    ::testing::Values(
        /*integer*/
        TestBalancedSlotsArith{1.2, default_epsil, vec_double{234.0, 0.0000001},
                               vec_double{241.0, 101.001}}));

}  // namespace
