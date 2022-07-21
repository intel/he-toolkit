// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Header file for encoder.
// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <vector>

inline constexpr double signnum(float x) { return (x > 0.0) - (x < 0.0); }

std::vector<int> gap(double theta, double bw, double epsil, int sz) {
  std::vector<int> res;
  std::vector<int> l;

  double sigma = signnum(theta);
  double t = std::abs(theta);
  long r;
  std::vector<double> a(sz, 0.0);
  for (double t = std::abs(theta); t > epsil;) {
    r = std::ceil(std::log(t) / std::log(bw));
    r -= (std::pow(bw, r) - t > t - std::pow(bw, r - 1));
    double t_minus_po = t - std::pow(bw, r);

    a[r + sz / 2] = sigma;
    sigma *= signnum(t_minus_po);
    t = std::abs(t_minus_po);
  }
  // We find the smallest exponent
  long tem = -sz / 2;
  while (a[tem + sz / 2] == 0) {
    tem += 1;
  }

  // We shift the exponents to turn it into a polynomial.
  std::vector<double> b(sz, 0.0);
  tem = std::min(tem, 0);

  for (int i = 0; i < sz / 2 - tem; ++i) {
    res[i] = a[i + tem + sz / 2];
  }

  return res;
}
