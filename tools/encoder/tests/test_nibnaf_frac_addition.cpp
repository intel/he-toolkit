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

// using TermsMap = std::map<long, long>;

// void comparePolyAndMap(const SparsePoly& poly, const TermsMap& terms_map) {
//  EXPECT_EQ(poly.size(), terms_map.size());
//  for (const auto& [index, coeff] : terms_map) {
//    EXPECT_EQ(poly[index], coeff);
//  }
// }

struct TestParamsSingleNumFrac {
  double num1;
  double num2;
  double rw;
  double epsil;
  long frac_degree;
};

class NIBNAFParamsSingleNumFracAddition
    : public testing::TestWithParam<TestParamsSingleNumFrac> {};

class NIBNAFSingleNumFrac : public testing::TestWithParam<double> {};

TEST_P(NIBNAFParamsSingleNumFracAddition, testCompareOriginalToDecodedEncoded) {
  NIBNAFCoder coder;
  auto& [num1, num2, rw, epsil, frac_degree] = GetParam();
  const auto& encoded1 = encode<SparsePoly>(
      num1, hekit::coder::NIBNAFCoder(rw, epsil, frac_degree));

  const auto& encoded2 = encode<SparsePoly>(
      num2, hekit::coder::NIBNAFCoder(rw, epsil, frac_degree));
  double decoded = coder.decode(encoded1 + encoded2);
  ASSERT_NEAR(num1 + num2, decoded, coder.epsilon());
}

double default_epsil = 1e-8;

INSTANTIATE_TEST_SUITE_P(variousParameters, NIBNAFParamsSingleNumFracAddition,
                         ::testing::Values(
                             /*integer*/
                             TestParamsSingleNumFrac{234.0, 241.0, 1.2,
                                                     default_epsil, 4096}));

}  // namespace
