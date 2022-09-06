// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <cmath>
#include <numeric>
#include <vector>

#include "coder.h"
#include "sparse_poly.h"

namespace hekit::coder {

inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

class NIBNAFCoder : public Coder<poly::SparsePoly, double> {
 public:
  // This ctor also cover the default ctor
  NIBNAFCoder(double rw = 1.2, double epsil = 1e-8, long frac_degree = 0L)
      : rw_(rw), epsil_(epsil), frac_degree_(frac_degree) {}

  ~NIBNAFCoder() = default;

  double epsilon() { return epsil_; }

  EncPoly<poly::SparsePoly> encode(const double& num) const override {
    const double log_rw_ = std::log(rw_);
    poly::SparsePoly a;
    long r;
    double t_minus_po;
    for (double t = std::abs(num), sigma = signum(num); t >= epsil_;
         t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
      r = std::ceil(std::log(t) / log_rw_);
      r -= (std::pow(rw_, r) - t > t - std::pow(rw_, r - 1));

      a[r] = sigma;
      t_minus_po = t - std::pow(rw_, r);
    }

    long first_index = a.begin()->first;
    long frac_exp =
        (a.degree() == 0) ? 0 : (first_index - std::abs(first_index)) / 2;

    if (frac_degree_ > 0) return EncPoly{laurentFracEncode(a), {}};
    return EncPoly{laurentEncode(a, frac_exp), {frac_exp}};
  }

  double decode(const EncPoly<poly::SparsePoly>& en) const override {
    const auto& poly = en.poly();
    if (frac_degree_ > 0) {
      // frac_degree_ power of 2
      auto laurentFracEncode = [this, midpoint = frac_degree_ / 2](
                                   double init, const auto& pair) {
        if (pair.first > midpoint)
          return init - pair.second * std::pow(this->rw_,
                                               pair.first - this->frac_degree_);
        return init + pair.second * std::pow(this->rw_, pair.first);
      };
      return std::accumulate(poly.begin(), poly.end(), 0.0, laurentFracEncode);
    }

    auto laurentDecode = [this, i = en.i().front()](double init,
                                                    const auto& pair) {
      return init + pair.second * std::pow(this->rw_, pair.first + i);
    };
    return std::accumulate(poly.begin(), poly.end(), 0.0, laurentDecode);
  }

 private:
  // The polynomial representation for fractional decoding, where a power of 2
  // cyclotomic is used x^-i is replaced by -x^(frac_degree-i), where
  // frac_degree is the degree of the cyclotomic.
  poly::SparsePoly laurentFracEncode(
      const poly::SparsePoly& sparse_poly) const {
    poly::SparsePoly poly_map;
    for (const auto& [key, value] : sparse_poly) {
      if (key < 0)
        poly_map[key + frac_degree_] = -value;
      else
        poly_map[key] = value;
    }
    return poly_map;
  }

  poly::SparsePoly laurentEncode(const poly::SparsePoly& sparse_poly,
                                 long i) const {
    poly::SparsePoly poly_map;
    for (const auto& [key, value] : sparse_poly) {
      poly_map[key - i] = value;
    }
    return poly_map;
  }

  double rw_;
  double epsil_;
  long frac_degree_;
};

}  // namespace hekit::coder
