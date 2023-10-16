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
    return FractionalEncodedPoly{this->m_poly + other.m_poly};
  }

  FractionalEncodedPoly operator*(const FractionalEncodedPoly& other) const {
    return FractionalEncodedPoly{this->m_poly * other.m_poly};
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
  Coder() = delete;
  explicit Coder(const FractionalParams& params) : m_params(params) {}

  auto params() const { return m_params; }

  FractionalEncodedPoly<SparsePoly> encode(double num) const {
    const auto [rw, epsil, _] = m_params;
    return FractionalEncodedPoly{
        encodeLaurentToFractional(encodeNumToLaurent(num, rw, epsil))};
  }

  double decode(const FractionalEncodedPoly<SparsePoly>& encoded_poly) const {
    const auto& poly = encoded_poly.poly();
    // frac_degree power of 2
    const auto [rw, _, frac_degree] = m_params;

    return std::accumulate(
        poly.cbegin(), poly.cend(), 0.0,
        [rw, frac_degree, midpoint = m_params.frac_degree / 2](
            double init, const auto& pair) {
          const auto [index, coeff] = pair;
          //      std::cerr << "init, mono: " << init << ", " << coeff << "x^"
          //      << index << std::endl;
          // SparsePoly does not truncate per se, but fractional encoding is
          // bound by the fractional degree.
          //          if (index >= frac_degree) return init;
          if (index > midpoint)  // fractional values
            return init - coeff * std::pow(rw, index - frac_degree);
          return init + coeff * std::pow(rw, index);
        });
  }

 private:
  FractionalParams m_params;

  // The polynomial representation for fractional decoding, where a power of 2
  // cyclotomic is used x^-i is replaced by -x^(frac_degree-i), where
  // frac_degree is the degree of the cyclotomic.
  SparsePoly encodeLaurentToFractional(const SparsePoly& sparse_poly) const {
    SparsePoly poly_map;
    for (const auto& [key, value] : sparse_poly) {
      if (key < 0)
        poly_map[key + m_params.frac_degree] = -value;
      else
        poly_map[key] = value;
    }
    return poly_map;
  }
};

}  // namespace hekit::coder
