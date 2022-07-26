// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <cmath>
#include <vector>
#incldue<map>
#include<iterator>

inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

inline std::map<long,long> gap(double theta, double bw, double epsil) {
  const double log_bw = std::log(bw);
   std::map<long, long> a;
  long r;
  double t_minus_po;
  for (double t = std::abs(theta), sigma = signum(theta); t > epsil;
       t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
    r = std::ceil(std::log(t) / log_bw);
    r -= (std::pow(bw, r) - t > t - std::pow(bw, r - 1));

    a[r] = sigma;
    t_minus_po = t - std::pow(bw, r);
  }
  return {a};
}
