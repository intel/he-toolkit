// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../nibnaf.h"

class NIBNAF : public ::testing::Test {
 protected:
  hekit::coder::NIBNAFCoder coder;
};

TEST_F(NIBNAF, test_integer) {
  double original = 546;
  const auto& encoded = coder.encode(original);
  double decoded = coder.decode(encoded);
  ASSERT_NEAR(original, decoded, coder.epsilon());
}

TEST_F(NIBNAF, test_double) {
  double original = 546.789;
  const auto& encoded = coder.encode(original);
  double decoded = coder.decode(encoded);
  ASSERT_NEAR(original, decoded, coder.epsilon());
}

TEST_F(NIBNAF, test_zero) {
  double original = 0;
  const auto& encoded = coder.encode(original);
  double decoded = coder.decode(encoded);
  ASSERT_NEAR(original, decoded, coder.epsilon());
}

// TEST_F(NIBNAF, test_integer) {
//  double num = 546;
//  const auto& en = coder.encode(num);
//  // Gets back the minimal negative exponent, the maximal degree and the
//  degree
//  // of the polynomial
//  long max_exp = en.poly().degree();
//  long deg = max_exp - en.i().front();
//  coder.print_out_results(en);
//  coder.print_poly_rep(en, en.i().front(), deg);
//  std::cout << '\n'
//            << std::fixed << std::setprecision(10) << coder.decode(en)
//            << std::endl;
//  ASSERT_TRUE(false);
//}

// TEST_F(NIBNAF, test_float) {
//   double num = 546.789;
//
//   const auto& en = coder.encode(num);
//   // Gets back the minimal negative exponent, the maximal degree and the
//   degree
//   // of the polynomial
//   long max_exp = en.poly().degree();
//   long deg = max_exp - en.i().front();
//   coder.print_out_results(en);
//   coder.print_poly_rep(en, en.i().front(), deg);
//   std::cout << '\n'
//             << std::fixed << std::setprecision(10) << coder.decode(en)
//             << std::endl;
//   ASSERT_TRUE(false);
// }

// TEST_F(NIBNAF, test_zero) {
//   double num = 0;
//
//   const auto& en = coder.encode(num);
//   // Gets back the minimal negative exponent, the maximal degree and the
//   degree
//   // of the polynomial
//   long max_exp = en.poly().degree();
//   long deg = max_exp - en.i().front();
//   coder.print_out_results(en);
//   std::cout << '\n';
//   coder.print_poly_rep(en, en.i().front(), deg);
//   std::cout << '\n'
//             << std::fixed << std::setprecision(10) << coder.decode(en)
//             << std::endl;
//   ASSERT_TRUE(false);
// }
