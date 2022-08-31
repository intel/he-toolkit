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
#include "sparse_poly.h"

namespace hekit::coder {

inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

class NIBNAFCoder : public Coder<poly::SparsePoly, double> {
 public:
  NIBNAFCoder() = default;

  NIBNAFCoder(double bw, double epsil) : bw_(bw), epsil_(epsil) {}

  ~NIBNAFCoder() = default;

  double epsilon() { return epsil_; }

  EncPoly<poly::SparsePoly> encode(const double& num) const override {
    const double log_bw_ = std::log(bw_);
    poly::SparsePoly a;
    long r;
    double t_minus_po;
    for (double t = std::abs(num), sigma = signum(num); t >= epsil_;
         t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
      r = std::ceil(std::log(t) / log_bw_);
      r -= (std::pow(bw_, r) - t > t - std::pow(bw_, r - 1));

      a[r] = sigma;
      t_minus_po = t - std::pow(bw_, r);
    }

    long first_index = a.begin()->first;
    long frac_exp =
        (a.degree() == 0) ? 0 : (first_index - std::abs(first_index)) / 2;
    return EncPoly{a, {frac_exp}};
  }

  double decode(const EncPoly<poly::SparsePoly>& en) const override {
    double sum = 0;
    for (const auto& [key, value] : en.poly()) {
      sum += value * std::pow(bw_, key);
    }
    return sum;
  }

 private:
  double bw_ = 1.2;
  double epsil_ = 0.00000001;
};

}  // namespace hekit::coder
