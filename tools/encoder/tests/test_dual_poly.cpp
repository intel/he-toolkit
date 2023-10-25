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

TEST_P(TestDualEncodeNum, testDecompRecomp) {
  const auto [rw, epsil, mod_pair, nums] = GetParam();
  auto dual_coder = DualCoder(BalancedSlotsParams{rw, epsil}, mod_pair);

  //  const auto encoded = coder.encode(original);
  //  double decoded = coder.decode(encoded);
}

INSTANTIATE_TEST_SUITE_P(singleNums, TestDualEncodeNum,
                         ::testing::Values(DualEncodeNum{
                             .rw = 1.2,
                             .epsil = 1e-8,
                             .mod_pair = {157, 257},
                             .nums = std::vector{0.0, 1.0, 2.5, 567.68, 1008.01,
                                                 -1.0, -256.16}}));

}  // namespace
