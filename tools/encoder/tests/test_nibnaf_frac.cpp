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

using TermsMap = std::map<long, long>;

void comparePolyAndMap(const SparsePoly& poly, const TermsMap& terms_map) {
  EXPECT_EQ(poly.size(), terms_map.size());
  for (const auto& [index, coeff] : terms_map) {
    EXPECT_EQ(poly[index], coeff);
  }
}

struct TestParamsSingleNumFrac {
  double num;
  double rw;
  double epsil;
  long frac_degree;
  TermsMap terms_map;
};

class NIBNAFParamsSingleNumFrac
    : public testing::TestWithParam<TestParamsSingleNumFrac> {};

class NIBNAFSingleNumFrac : public testing::TestWithParam<double> {};

TEST_P(NIBNAFSingleNumFrac, testCompareOriginalToDecodedEncoded) {
  NIBNAFCoder coder;
  double original = GetParam();
  const auto& encoded = coder.encode(original);
  double decoded = coder.decode(encoded);
  ASSERT_NEAR(original, decoded, coder.epsilon());
}

TEST_P(NIBNAFParamsSingleNumFrac, testRw) {
  auto& [num, rw, epsil, frac_degree, terms_map] = GetParam();
  const auto encoded = encode<SparsePoly>(
      num, hekit::coder::NIBNAFCoder{rw, epsil, frac_degree});
  comparePolyAndMap(encoded.poly(), terms_map);
}

INSTANTIATE_TEST_SUITE_P(variousSingleNumbers, NIBNAFSingleNumFrac,
                         // zero, integer_part, double
                         ::testing::Values(0, 546, 546.789, 23.456, 0.2345));
double default_epsil = 1e-8;

INSTANTIATE_TEST_SUITE_P(
    variousParameters, NIBNAFParamsSingleNumFrac,
    ::testing::Values(
        /*integer*/
        TestParamsSingleNumFrac{234.0,
                                1.2,
                                default_epsil,
                                4096,
                                {{7, -1},
                                 {30, 1},
                                 {3996, 1},
                                 {4010, -1},
                                 {4032, -1},
                                 {4054, -1},
                                 {4072, -1},
                                 {4087, -1}}},
        /*fraction*/
        // Extreme case. number<epsilon so it just gets encoded as "0".
        TestParamsSingleNumFrac{1e-9, 1.2, default_epsil, 4096, {}},
        TestParamsSingleNumFrac{0.2563,
                                1.2,
                                default_epsil,
                                4096,
                                {{4005, -1},
                                 {4023, 1},
                                 {4043, 1},
                                 {4058, 1},
                                 {4075, 1},
                                 {4089, -1}}},
        TestParamsSingleNumFrac{0.0023,
                                1.2,
                                default_epsil,
                                4096,
                                {{4008, 1}, {4030, 1}, {4047, 1}, {4063, -1}}},
        TestParamsSingleNumFrac{
            0.0000021, 1.2, default_epsil, 4096, {{4008, -1}, {4024, -1}}},
        /*double*/
        TestParamsSingleNumFrac{12.765,
                                1.2,
                                default_epsil,
                                4096,
                                {{4004, -1},
                                 {4022, -1},
                                 {4049, -1},
                                 {4065, -1},
                                 {4082, 1},
                                 {14, 1}}},
        TestParamsSingleNumFrac{65432982.000002,
                                1.2,
                                default_epsil,
                                4096,
                                {{4025, -1},
                                 {4039, 1},
                                 {4054, -1},
                                 {4076, -1},
                                 {4091, 1},
                                 {15, -1},
                                 {30, -1},
                                 {51, 1},
                                 {65, 1},
                                 {83, -1},
                                 {99, 1}}},
        /*Not the default rw*/
        //  TestParamsSingleNum{
        //      23456327,
        //      1.001,  // An extreme case, very small value for bw, should be
        //      very
        //              // sparse.
        //      {{0, 1}, {7639, -1}, {15325, -1}, {24792, 1}, {33709, 1}}},
        //   TestParamsSingleNum{0.00001, 1.001, {{0, 1}}},  // However i=11519
        TestParamsSingleNumFrac{231.2009,
                                2.0,
                                default_epsil,
                                4096,
                                {{4070, 1},
                                 {4072, 1},
                                 {4076, -1},
                                 {4077, -1},
                                 {4081, 1},
                                 {4084, 1},
                                 {4087, 1},
                                 {4090, -1},
                                 {4092, 1},
                                 {4094, -1},
                                 {0, -1},
                                 {3, 1},
                                 {5, -1},
                                 {8, 1}}}));

}  // namespace
