// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// A program that calls the header and returns the coefficients and the
// corresponding exponents.
#include <iostream>
#include <iterator>
#include <map>

#include "nibnaf.h"

template <typename T>
void print_out_results(const T& en) {
  for (const auto& [key, value] : en) {
    std::cout << "(" << key << " , " << value << ")" << std::endl;
  }
}

void test_integer() {
  double number = 546;
  double bw = 2;
  double epsil = 0.4;
  
  const auto en = gap(number, bw, epsil);
  print_out_results(en);
}

void test_float() {
  double number = 546.789;
  double bw = 2;
  double epsil = 0.4;

  const auto en = gap(number, bw, epsil);
  print_out_results(en);
}

void test_zero() {
  double number = 0;
  double bw = 2;
  double epsil = 0.4;
  
  const auto en = gap(number, bw, epsil);
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
