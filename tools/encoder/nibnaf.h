// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <cmath>
#include <vector>

inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

inline std::vector<long> gap(double theta, double bw, double epsil, long sz) {
  const double log_bw = std::log(bw);
  std::vector<double> a(sz, 0.0);
  long r;
  double t_minus_po;
  for (double t = std::abs(theta), sigma = signum(theta); t > epsil;
       t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
    r = std::ceil(std::log(t) / log_bw);
    r -= (std::pow(bw, r) - t > t - std::pow(bw, r - 1));

    a[r + sz / 2] = sigma;
    t_minus_po = t - std::pow(bw, r);
  }

  // Find the smallest exponent
  const auto it = std::find_if(a.begin(), a.begin() + sz / 2,
                               [](double num) { return num != 0.0; });

  // Shift the exponents to turn it into a polynomial
  return {it, a.end()};
}
