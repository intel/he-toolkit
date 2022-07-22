// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Header file for encoder.
// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <cmath>
#include <vector>

inline constexpr double signnum(double x) { return (x > 0.0) - (x < 0.0); }

inline std::vector<long> gap(double theta, double bw, double epsil, long sz) {
  double sigma = signnum(theta);

  std::vector<double> a(sz, 0.0);
  for (double t = std::abs(theta); t > epsil;) {
    long r = std::ceil(std::log(t) / std::log(bw));
    r -= (std::pow(bw, r) - t > t - std::pow(bw, r - 1));
    double t_minus_po = t - std::pow(bw, r);

    a[r + sz / 2] = sigma;
    sigma *= signnum(t_minus_po);
    t = std::abs(t_minus_po);
  }

  // Find the smallest exponent
  const auto it = std::find_if(a.begin(), a.begin() + sz / 2,
                               [](double num) { return num != 0.0; });

  // Shift the exponents to turn it into a polynomial
  return {it, a.end()};
}
