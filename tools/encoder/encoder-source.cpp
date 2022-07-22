// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// A program that calls the header and returns the coefficients and the
// corresponding exponents.
#include <iostream>

#include "nibnaf.h"

template <typename T>
void print_out_results(const T& en) {
  for (long i = 0; i < en.size(); ++i)
    if (en[i] != 0) std::cout << en[i] << ", " << i << std::endl;
}

void test_integer() {
  double number = 546;
  double bw = 2;
  double epsil = 0.4;
  long sz = 200;

  const auto en = gap(number, bw, epsil, sz);
  print_out_results(en);
}

void test_float() {
  double number = 546.789;
  double bw = 2;
  double epsil = 0.4;
  long sz = 200;

  const auto en = gap(number, bw, epsil, sz);
  print_out_results(en);
}

void test_zero() {
  double number = 0;
  double bw = 2;
  double epsil = 0.4;
  long sz = 200;

  const auto en = gap(number, bw, epsil, sz);
  print_out_results(en);
}

int main(void) {
  std::cout << "test float\n";
  test_float();
  std::cout << "test integer\n";
  test_integer();
  std::cout << "test zero\n";
  test_zero();

  return 0;
}
