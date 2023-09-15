
// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../nibnaf.h"

namespace {

using hekit::coder::encode;
using hekit::coder::NIBNAFCoder;
using hekit::poly::SparsePoly;
using vec_double = std::vector<double>;

struct TestParamsMultiNum {
  std::vector<double> nums;
  double rw;
};

class NIBNAFParamsMultiNum : public testing::TestWithParam<TestParamsMultiNum> {
};

class NIBNAFMultiNum : public testing::TestWithParam<std::vector<double>> {};

TEST_P(NIBNAFMultiNum, testCompareOriginalToDecodedEncoded) {
  NIBNAFCoder coder;
  const auto& original = GetParam();
  const auto& encoded = coder.encode(original);
  const auto& is = encoded.i();
  for (int i = 0; i < original.size(); ++i) std::cout << is[i] << std::endl;
  const auto decoded = coder.decode(encoded);

  for (int i = 0; i < original.size(); ++i)
    ASSERT_NEAR(original[0], decoded[0], coder.epsilon());
}

INSTANTIATE_TEST_SUITE_P(
    variousSingleNumbers, NIBNAFMultiNum,
    // zero, integer_part, double
    ::testing::Values(vec_double{0.0, 1.2, 0.235, 12.3, 546, 546.789},
                      vec_double{21, 2.987, 5.678},
                      vec_double{0.000000001, 12345, 2345.987}));
}  // namespace
