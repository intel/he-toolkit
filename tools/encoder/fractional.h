// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <cmath>
#include <numeric>
#include <utility>

#include "coder.h"
#include "sparse_poly.h"

namespace hekit::coder {

// PolyType could be anything that represents a polynomial
// i.e. Ctxt, Ptxt, a user defined object that must have + and * ops defined
template <typename Poly>
class FractionalEncodedPoly {
 public:
  FractionalEncodedPoly() = default;
  explicit FractionalEncodedPoly(const Poly& poly) : m_poly(poly) {}
  FractionalEncodedPoly operator+(const FractionalEncodedPoly& other) const {
    FractionalEncodedPoly sum;
    sum.m_poly = this->m_poly + other.m_poly;
    return sum;
  }

  FractionalEncodedPoly operator*(const FractionalEncodedPoly& other) const {
    FractionalEncodedPoly prod;
    prod.m_poly = this->m_poly * other.m_poly;
    return prod;
  }

  Poly poly() const { return m_poly; }

 private:
  Poly m_poly;
};

struct FractionalParams {
  double rw;
  double epsil;
  long frac_degree;
};

template <>
class Coder<FractionalParams> {
 public:
  explicit Coder(const FractionalParams& params) : m_params(params) {}

  FractionalEncodedPoly<SparsePoly> encode(double num) const {
    const auto [a, _] = EncodeHelper(num);
    return FractionalEncodedPoly{laurentEncode(a)};
  }

  double decode(const FractionalEncodedPoly<SparsePoly>& encoded_poly) const {
    const auto& poly = encoded_poly.poly();
    // frac_degree_ power of 2
    auto laurentDecode = [this, midpoint = m_params.frac_degree / 2](
                             double init, const auto& pair) {
      const auto [rw, epsil, frac_degree] = m_params;
      if (pair.first > midpoint)
        return init - pair.second * std::pow(rw, pair.first - frac_degree);
      return init + pair.second * std::pow(rw, pair.first);
    };
    return std::accumulate(poly.begin(), poly.end(), 0.0, laurentDecode);
  }

 private:
  FractionalParams m_params;

  // The polynomial representation for fractional decoding, where a power of 2
  // cyclotomic is used x^-i is replaced by -x^(frac_degree-i), where
  // frac_degree is the degree of the cyclotomic.
  SparsePoly laurentEncode(const SparsePoly& sparse_poly) const {
    SparsePoly poly_map;
    for (const auto& [key, value] : sparse_poly) {
      if (key < 0)
        poly_map[key + m_params.frac_degree] = -value;
      else
        poly_map[key] = value;
    }
    return poly_map;
  }

  // TODO Refactor this a common code
  std::pair<SparsePoly, long> EncodeHelper(double num) const {
    const auto [rw, epsil, _] = m_params;
    const double log_rw = std::log(m_params.rw);
    SparsePoly a;
    long r;
    double t_minus_po;
    for (double t = std::abs(num), sigma = signum(num); t >= epsil;
         t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
      r = std::ceil(std::log(t) / log_rw);
      r -= (std::pow(rw, r) - t > t - std::pow(rw, r - 1));

      a[r] = sigma;
      t_minus_po = t - std::pow(rw, r);
    }

    long first_index = a.begin()->first;
    long frac_exp =
        (a.degree() == 0) ? 0 : (first_index - std::abs(first_index)) / 2;
    return std::pair{a, frac_exp};
  }
};

}  // namespace hekit::coder
