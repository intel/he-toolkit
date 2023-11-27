// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../balanced.h"
#include "../npoly.h"

namespace {

using hekit::coder::BalancedParams;
using hekit::coder::BalancedSlotsEncodedPoly;
using hekit::coder::BalancedSlotsParams;
using hekit::coder::NCoder;

struct DualEncodeNum {
  double rw;
  double epsil;
  std::vector<long> mod_pair;
  std::vector<double> nums;
};

class TestDualEncodeNum : public testing::TestWithParam<DualEncodeNum> {};

TEST_P(TestDualEncodeNum, testDecompRecompBalanced) {
  const auto [rw, epsil, mod_pair, nums] = GetParam();
  auto ncoder = NCoder<BalancedParams>(BalancedParams{rw, epsil}, mod_pair);

  // TODO better than just first num
  const auto encoded = ncoder.encode(nums[0]);
  const auto decoded = ncoder.decode(encoded);

  EXPECT_NEAR(decoded, nums[0], epsil);
}

TEST_P(TestDualEncodeNum, testDecompRecompBalancedSlots) {
  const auto [rw, epsil, mod_pair, nums] = GetParam();
  auto ncoder = NCoder(BalancedSlotsParams{rw, epsil}, mod_pair);

  const auto encoded = ncoder.encode(nums);
  const auto decoded = ncoder.decode(encoded);

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
  std::vector<long> mod_pair;
  std::vector<double> a_nums;
  std::vector<double> b_nums;
};

class TestDualEncodeOps : public testing::TestWithParam<DualEncodeTwoNum> {};

TEST_P(TestDualEncodeOps, testAdd) {
  const auto [rw, epsil, mod_pair, a_nums, b_nums] = GetParam();
  auto ncoder = NCoder(BalancedSlotsParams{rw, epsil}, mod_pair);

  const auto a_encoded = ncoder.encode(a_nums);
  const auto b_encoded = ncoder.encode(b_nums);

  const auto sum_encoded = a_encoded + b_encoded;

  const auto decoded = ncoder.decode(sum_encoded);

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
  auto ncoder = NCoder(BalancedSlotsParams{rw, epsil}, mod_pair);

  const auto a_encoded = ncoder.encode(a_nums);
  const auto b_encoded = ncoder.encode(b_nums);

  const auto sum_encoded = a_encoded * b_encoded;

  const auto decoded = ncoder.decode(sum_encoded);

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
                             .mod_pair = std::vector{157L, 257L},
                             .a_nums = std::vector{0.0, 1.0, 2.5, 567.68,
                                                   1008.01, -1.0, -256.16},
                             .b_nums = std::vector{0.0, 1.0, 3.4, -301.54,
                                                   789.99678, -1.115, 20.20}}));

}  // namespace
