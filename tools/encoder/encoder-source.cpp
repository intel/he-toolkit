// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// A program that calls the header and returns the coefficients and the
// corresponding exponents.
#include <iostream>
#include <iterator>
#include <map>

#include "iomanip"
#include "nibnaf.h"

// To print the zero polynomial and the zero results when en is empty, which
// happens when theta=0 or |theta|<epsil
inline void print_zero_pol() { std::cout << "0"; }
inline void print_zero_res() { std::cout << "(0,0)"; }

void test_integer() {
  Coder co;
  double num = 546;

  const auto en = co.encode(num);
  // Gets back the minimal negative exponent, the maximal degree and the degree
  // of the polynomial
  long frac_exp = (en.begin()->first - std::abs(en.begin()->first)) / 2;
  long max_exp = std::prev(en.end())->first;
  long deg = max_exp - frac_exp;
  co.print_out_results(en);
  co.print_poly_rep(en, frac_exp, deg);
  std::cout << std::endl;
  std::cout << std::fixed << std::setprecision(10) << co.decoder(en)
            << std::endl;
}

void test_float() {
  Coder co;
  double num = 546.789;

  const auto en = co.encode(num);
  // Gets back the minimal negative exponent, the maximal degree and the degree
  // of the polynomial
  long frac_exp = (en.begin()->first - std::abs(en.begin()->first)) / 2;
  long max_exp = std::prev(en.end())->first;
  long deg = max_exp - frac_exp;
  co.print_out_results(en);
  co.print_poly_rep(en, frac_exp, deg);
  std::cout << std::endl;
  std::cout << std::fixed << std::setprecision(10) << co.decoder(en)
            << std::endl;
}

void test_zero() {
  Coder co;
  double num = 0;

  const auto en = co.encode(num);
  // Gets back the minimal negative exponent, the maximal degree and the degree
  // of the polynomial
  long frac_exp =
      en.empty() ? 0 : (en.begin()->first - std::abs(en.begin()->first)) / 2;
  long max_exp = en.empty() ? 0 : std::prev(en.end())->first;
  long deg = max_exp - frac_exp;
  en.empty() ? print_zero_res() : co.print_out_results(en);
  std::cout << std::endl;
  en.empty() ? print_zero_pol() : co.print_poly_rep(en, frac_exp, deg);
  std::cout << std::endl;
  std::cout << std::fixed << std::setprecision(10) << co.decoder(en)
            << std::endl;
}

int main(void) {
  Coder co;
  std::cout << "test float\n";
  test_float();
  std::cout << "test integer\n";
  test_integer();
  std::cout << "test zero\n";
  test_zero();

  return 0;
}
