// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include "sparse_poly.h"

namespace hekit::coder {

// specialisations are kept in the appropriate scheme files
template <typename Scheme>
class Coder {
  // Specialisations only
  static_assert(!std::is_same<Scheme, Scheme>(),
                "Only allowed schemes can be used");
  // Pointless ctor is required for CTAD
  explicit Coder(const Scheme& params) {}
};

// TODO move to more appropriate header?
inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

inline SparsePoly encodeNumToLaurent(double num, double rw, double epsil) {
  const double log_rw = std::log(rw);
  SparsePoly a_poly;
  long r;
  double t_minus_po;
  for (double t = std::abs(num), sigma = signum(num); t >= epsil;
       t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
    r = std::ceil(std::log(t) / log_rw);
    r -= (std::pow(rw, r) - t > t - std::pow(rw, r - 1));

    a_poly[r] = sigma;
    t_minus_po = t - std::pow(rw, r);
  }

  return a_poly;
}

inline long computeFracExp(const SparsePoly& a) {
  long first_index = a.begin()->first;
  long frac_exp =
      (a.degree() == 0) ? 0 : (first_index - std::abs(first_index)) / 2;
  return frac_exp;
}

}  // namespace hekit::coder
