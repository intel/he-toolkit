// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// A source file that calls the header and returns the coefficients and the
// corresponding exponents.
#include <array>
#include <iostream>

#include "nibnaf.h"

int main() {
  double theta, bw, epsil;
  long sz;
  std::cout << "Enter the number to encode:";
  std::cin >> theta;
  std::cout << "Enter the base to encode:";
  std::cin >> bw;
  std::cout << "Enter the amount of precision:";
  std::cin >> epsil;
  std::cout << "Enter the size of the array:";
  std::cin >> sz;

  const auto en = gap(theta, bw, epsil, sz);

  for (long i = 0; i < sz; ++i)
    if (en[i] != 0) std::cout << en[i] << ", " << i << std::endl;

  return 0;
}
