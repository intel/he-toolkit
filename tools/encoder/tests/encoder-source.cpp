// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// A program that calls the header and returns the coefficients and the
// corresponding exponents.
#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <iterator>
#include <map>

#include "../nibnaf.h"

TEST(NIBNAF, test_integer) {
  hekit::coder::NIBNAFCoder co;
  double num = 546;

  const auto& en = co.encode(num);
  // Gets back the minimal negative exponent, the maximal degree and the degree
  // of the polynomial
  long max_exp = en.poly().degree();
  long deg = max_exp - en.i().front();
  co.print_out_results(en);
  co.print_poly_rep(en, en.i().front(), deg);
  std::cout << '\n'
            << std::fixed << std::setprecision(10) << co.decode(en)
            << std::endl;
  ASSERT_TRUE(false);
}

TEST(NIBNAF, test_float) {
  hekit::coder::NIBNAFCoder co;
  double num = 546.789;

  const auto& en = co.encode(num);
  // Gets back the minimal negative exponent, the maximal degree and the degree
  // of the polynomial
  long max_exp = en.poly().degree();
  long deg = max_exp - en.i().front();
  co.print_out_results(en);
  co.print_poly_rep(en, en.i().front(), deg);
  std::cout << '\n'
            << std::fixed << std::setprecision(10) << co.decode(en)
            << std::endl;
  ASSERT_TRUE(false);
}

TEST(NIBNAF, test_zero) {
  hekit::coder::NIBNAFCoder co;
  double num = 0;

  const auto& en = co.encode(num);
  // Gets back the minimal negative exponent, the maximal degree and the degree
  // of the polynomial
  long max_exp = en.poly().degree();
  long deg = max_exp - en.i().front();
  co.print_out_results(en);
  std::cout << '\n';
  co.print_poly_rep(en, en.i().front(), deg);
  std::cout << '\n'
            << std::fixed << std::setprecision(10) << co.decode(en)
            << std::endl;
  ASSERT_TRUE(false);
}
