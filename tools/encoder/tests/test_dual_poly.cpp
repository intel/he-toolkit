// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../balanced.h"
#include "../dual_poly.h"

namespace {

using hekit::coder::BalancedSlotsEncodedPoly;
using hekit::coder::BalancedSlotsParams;
using hekit::coder::DualCoder;

struct DualEncodeNum {
  double rw;
  double epsil;
  std::pair<long, long> mod_pair;
  std::vector<double> nums;
};

class TestDualEncodeNum : public testing::TestWithParam<DualEncodeNum> {};

TEST_P(TestDualEncodeNum, testDecompRecompBalancedSlots) {
  const auto [rw, epsil, mod_pair, nums] = GetParam();
  auto dual_coder = DualCoder(BalancedSlotsParams{rw, epsil}, mod_pair);

  const auto encoded = dual_coder.encode(nums);
  const auto decoded = dual_coder.decode(encoded);

  for (long i = 0; i < nums.size(); ++i)
    EXPECT_NEAR(decoded[i], nums[i], epsil);
}

INSTANTIATE_TEST_SUITE_P(singleNums, TestDualEncodeNum,
                         ::testing::Values(DualEncodeNum{
                             .rw = 1.2,
                             .epsil = 1e-8,
                             .mod_pair = {157, 257},
                             .nums = std::vector{0.0, 1.0, 2.5, 567.68, 1008.01,
                                                 -1.0, -256.16}}));

struct DualEncodeTwoNum {
  double rw;
  double epsil;
  std::pair<long, long> mod_pair;
  std::vector<double> a_nums;
  std::vector<double> b_nums;
};

class TestDualEncodeOps : public testing::TestWithParam<DualEncodeTwoNum> {};

TEST_P(TestDualEncodeOps, testAdd) {
  const auto [rw, epsil, mod_pair, a_nums, b_nums] = GetParam();
  auto dual_coder = DualCoder(BalancedSlotsParams{rw, epsil}, mod_pair);

  const auto a_encoded = dual_coder.encode(a_nums);
  const auto b_encoded = dual_coder.encode(b_nums);

  const auto sum_encoded = a_encoded + b_encoded;

  const auto decoded = dual_coder.decode(sum_encoded);

  for (long i = 0; i < a_nums.size(); ++i) {
    const auto& a_num = a_nums[i];
    const auto& b_num = b_nums[i];
    EXPECT_NEAR(decoded[i], a_num + b_num, 2 * epsil)
        << "a = " << a_num << ", b = " << b_num
        << ", a + b = " << a_num + b_num;
  }
}

TEST_P(TestDualEncodeOps, testMult) {
  const auto [rw, epsil, mod_pair, a_nums, b_nums] = GetParam();
  auto dual_coder = DualCoder(BalancedSlotsParams{rw, epsil}, mod_pair);

  const auto a_encoded = dual_coder.encode(a_nums);
  const auto b_encoded = dual_coder.encode(b_nums);

  const auto sum_encoded = a_encoded * b_encoded;

  const auto decoded = dual_coder.decode(sum_encoded);

  for (long i = 0; i < a_nums.size(); ++i) {
    const auto& a_num = a_nums[i];
    const auto& b_num = b_nums[i];
    EXPECT_NEAR(decoded[i], a_num * b_num,
                (std::abs(a_num) + std::abs(b_num)) * epsil)
        << "a = " << a_num << ", b = " << b_num
        << ", a + b = " << a_num + b_num;
  }
}

INSTANTIATE_TEST_SUITE_P(twoNums, TestDualEncodeOps,
                         ::testing::Values(DualEncodeTwoNum{
                             .rw = 1.2,
                             .epsil = 1e-8,
                             .mod_pair = {157, 257},
                             .a_nums = std::vector{0.0, 1.0, 2.5, 567.68,
                                                   1008.01, -1.0, -256.16},
                             .b_nums = std::vector{0.0, 1.0, 3.4, -301.54,
                                                   789.99678, -1.115, 20.20}}));

}  // namespace
