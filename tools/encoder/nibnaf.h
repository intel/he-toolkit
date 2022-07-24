// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <cmath>
#include <vector>

#include "coder.h"

namespace Coder {

inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

// TODO
inline constexpr double poly_eval(const PolyRep& poly_rep, double base) {
  // Expand base
  // inner product
  return 0.0;
}

class rwNIBNAFCoder : public Coder {
 public:
  rwNIBNAFCoder(double bw, double epsil, long sz)
      : bw(bw), epsil(epsil), sz(sz) {}
  PolyRep encode(double num) const override {
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

  double decode(const PolyRep& poly_rep) const override {
    return poly_eval(poly_rep, bw);
  }

  ~rwNIBNAFCoder() = default;

 private:
  double bw;     // the b_w base
  double epsil;  // absolute error tolerance
  long sz;       // array/poly size
};

}  // namespace Coder
