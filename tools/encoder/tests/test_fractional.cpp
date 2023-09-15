// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../fractional.h"

namespace {

using hekit::coder::Coder;
using hekit::coder::FractionalParams;
using hekit::coder::SparsePoly;

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

class ParamsSingleNumFrac
    : public testing::TestWithParam<TestParamsSingleNumFrac> {};

class SingleNumFrac : public testing::TestWithParam<double> {};

TEST_P(SingleNumFrac, testCompareOriginalToDecodedEncoded) {
  const auto params =
      FractionalParams{.rw = 1.2, .epsil = 1e-8, .frac_degree = 4096};
  Coder coder(params);
  double original = GetParam();
  const auto& encoded = coder.encode(original);
  double decoded = coder.decode(encoded);
  ASSERT_NEAR(original, decoded, params.epsil);
}

TEST_P(ParamsSingleNumFrac, testRw) {
  auto& [num, rw, epsil, frac_degree, terms_map] = GetParam();
  const auto encoded =
      Coder<FractionalParams>({rw, epsil, frac_degree}).encode(num);
  comparePolyAndMap(encoded.poly(), terms_map);
}

INSTANTIATE_TEST_SUITE_P(variousSingleNumbers, SingleNumFrac,
                         // zero, integer_part, double
                         ::testing::Values(0, 546, 546.789, 23.456, 0.2345));
double default_epsil = 1e-8;

INSTANTIATE_TEST_SUITE_P(
    variousParameters, ParamsSingleNumFrac,
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

struct TestParamsTwoNums {
  double num1;
  double num2;
  double rw;
  double epsil;
  long frac_degree;
};

class ParamsSingleNumFracAddition
    : public testing::TestWithParam<TestParamsTwoNums> {};

TEST_P(ParamsSingleNumFracAddition, testCompareOriginalToDecodedEncoded) {
  auto& [num1, num2, rw, epsil, frac_degree] = GetParam();

  FractionalParams params{rw, epsil, frac_degree};
  Coder coder(params);
  const auto& encoded1 = coder.encode(num1);
  const auto& encoded2 = coder.encode(num2);
  double decoded = coder.decode(encoded1 + encoded2);
  ASSERT_NEAR(num1 + num2, decoded, params.epsil);
}

INSTANTIATE_TEST_SUITE_P(variousParameters, ParamsSingleNumFracAddition,
                         ::testing::Values(
                             /*integer*/
                             TestParamsTwoNums{234.0, 241.0, 1.2, default_epsil,
                                               4096L}));

}  // namespace
