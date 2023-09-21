// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../balanced.h"

namespace {

using hekit::coder::BalancedParams;
using hekit::coder::Coder;
using hekit::coder::SparsePoly;

using TermsMap = std::map<long, long>;

void comparePolyAndMap(const SparsePoly& poly, const TermsMap& terms_map) {
  EXPECT_EQ(poly.size(), terms_map.size());
  for (const auto& [index, coeff] : poly) {
    EXPECT_EQ(terms_map.at(index), coeff);
  }
}

struct TestParamsSingleNum {
  double num;
  double rw;
  TermsMap terms_map;
};

class ParamsSingleNum : public testing::TestWithParam<TestParamsSingleNum> {};

class SingleNum : public testing::TestWithParam<double> {};

TEST_P(SingleNum, testCompareOriginalToDecodedEncoded) {
  auto params = BalancedParams{.rw = 1.2, .epsil = 1e-8};
  auto coder = Coder(params);
  double original = GetParam();
  const auto& encoded = coder.encode(original);
  double decoded = coder.decode(encoded);
  ASSERT_NEAR(original, decoded, params.epsil);
}

TEST_P(ParamsSingleNum, testRw) {
  auto& [num, rw, terms_map] = GetParam();
  Coder<BalancedParams> coder({rw, 1e-8});
  auto encoded = coder.encode(num);
  comparePolyAndMap(encoded.poly(), terms_map);
}

INSTANTIATE_TEST_SUITE_P(variousSingleNumbers, SingleNum,
                         // zero, integer_part, double
                         ::testing::Values(0, 546, 546.789));

INSTANTIATE_TEST_SUITE_P(
    variousParameters, ParamsSingleNum,
    ::testing::Values(
        /*integer*/
        TestParamsSingleNum{234.0,
                            1.2,
                            {{0, -1},
                             {14, 1},
                             {36, 1},
                             {58, 1},
                             {76, 1},
                             {91, 1},
                             {107, -1},
                             {130, 1}}},
        /*fraction*/
        // Extreme case. number<epsilon so it just gets encoded as "0".
        TestParamsSingleNum{1e-9, 1.2, {}},
        TestParamsSingleNum{
            0.2563,
            1.2,
            {{0, 1}, {18, -1}, {38, -1}, {53, -1}, {70, -1}, {84, 1}}},
        TestParamsSingleNum{
            0.0023, 1.2, {{0, -1}, {22, -1}, {39, -1}, {55, 1}}},
        TestParamsSingleNum{0.0000021, 1.2, {{0, 1}, {16, 1}}},
        /*double*/
        TestParamsSingleNum{
            12.765,
            1.2,
            {{0, 1}, {18, 1}, {45, 1}, {61, 1}, {78, -1}, {106, 1}}},
        TestParamsSingleNum{65432982.000002,
                            1.2,
                            {{0, 1},
                             {14, -1},
                             {29, 1},
                             {51, 1},
                             {66, -1},
                             {86, -1},
                             {101, -1},
                             {122, 1},
                             {136, 1},
                             {154, -1},
                             {170, 1}}},
        /*Not the default rw*/
        TestParamsSingleNum{
            23456327,
            1.001,  // An extreme case, very small value for bw, should be very
                    // sparse.
            {{0, 1}, {7639, -1}, {15325, -1}, {24792, 1}, {33709, 1}}},
        TestParamsSingleNum{0.00001, 1.001, {{0, 1}}},  // However i=11519
        TestParamsSingleNum{231.2009,
                            2.0,
                            {{0, -1},
                             {2, -1},
                             {6, 1},
                             {7, 1},
                             {11, -1},
                             {14, -1},
                             {17, -1},
                             {20, 1},
                             {22, -1},
                             {24, 1},
                             {26, -1},
                             {29, 1},
                             {31, -1},
                             {34, 1}}}));

struct TestParamsSingleNumBalanced {
  double num1;
  double num2;
  double rw;
  double epsil;
};

class ParamsSingleNumBalanced
    : public testing::TestWithParam<TestParamsSingleNumBalanced> {};

TEST_P(ParamsSingleNumBalanced, testBalancedAddition) {
  auto& [num1, num2, rw, epsil] = GetParam();

  BalancedParams params{rw, epsil};
  Coder coder(params);
  const auto& encoded1 = coder.encode(num1);
  const auto& encoded2 = coder.encode(num2);
  double decoded = coder.decode(encoded1 + encoded2);

  ASSERT_NEAR(num1 + num2, decoded, epsil);
}

TEST_P(ParamsSingleNumBalanced, testBalancedMultiplication) {
  auto& [num1, num2, rw, epsil] = GetParam();

  BalancedParams params{rw, epsil};
  Coder coder(params);
  const auto& encoded1 = coder.encode(num1);
  const auto& encoded2 = coder.encode(num2);
  double decoded = coder.decode(encoded1 * encoded2);

  ASSERT_NEAR(num1 * num2, decoded, epsil);
}

double default_epsil = 1e-8;

INSTANTIATE_TEST_SUITE_P(variousParameters, ParamsSingleNumBalanced,
                         ::testing::Values(
                             /*integer*/
                             TestParamsSingleNumBalanced{234.0, 241.0, 1.2,
                                                         default_epsil}));

}  // namespace
