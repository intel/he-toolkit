// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <algorithm>
#include <cmath>
#include <functional>
#include <numeric>
#include <utility>
#include <vector>

#include "coder.h"
#include "sparse_poly.h"

namespace hekit::coder {

struct BalancedParams {
  double rw;
  double epsil;
};

struct BalancedSlotsParams {
  double rw;
  double epsil;
};

// PolyType could be anything that represents a polynomial
// i.e. Ctxt, Ptxt, a user defined object that must have + and * ops defined
template <typename PolyType>
class BalancedEncodedPoly {
 public:
  BalancedEncodedPoly() = delete;
  BalancedEncodedPoly(const PolyType& poly, long digit)
      : m_poly(poly), m_digit(digit) {}

  BalancedEncodedPoly operator+(const BalancedEncodedPoly& other) const {
    auto ans = other;
    if (this->m_digit < other.m_digit) {
      ans.m_poly =
          this->m_poly + shift(other.m_poly, other.m_digit - this->m_digit);
      ans.m_digit = this->m_digit;
    } else {
      ans.m_poly =
          other.m_poly + shift(this->m_poly, this->m_digit - other.m_digit);
    }
    return ans;
  }

  BalancedEncodedPoly operator*(const BalancedEncodedPoly& other) const {
    auto ans = other;
    ans.m_poly = this->m_poly * other.m_poly;
    ans.m_digit = this->m_digit + other.m_digit;
    return ans;
  }

  PolyType poly() const { return m_poly; }
  long digit() const { return m_digit; }

 private:
  PolyType m_poly;
  long m_digit;
};

template <typename PolyType>
class BalancedSlotsEncodedPoly {
  BalancedSlotsEncodedPoly() = delete;
  BalancedSlotsEncodedPoly(const PolyType& poly,
                           const std::vector<long>& digits)
      : m_poly(poly), m_digits(digits) {}

 public:
  BalancedSlotsEncodedPoly operator+(const BalancedSlotsEncodedPoly& other) {
    auto ans = other;
    std::transform(this->m_digits.cbegin(), this->m_digits.cend(),
                   other.m_digits.cbegin(), ans.m_digits.begin(),
                   [](auto x, auto y) { return (x < y) ? x : y; });
    // TODO
    //{
    //  ans.m_poly = this->m_poly + shift(other.m_poly, other.m_digits -
    //  this->m_digits);
    //} else {
    //  ans.m_poly = other.m_poly + shift(this->m_poly, this->m_digits -
    //  other.m_digits);
    //}
    return ans;
  }

  BalancedSlotsEncodedPoly operator*(const BalancedSlotsEncodedPoly& other) {
    auto ans = other;
    ans.m_poly = this->m_poly * other.m_poly;
    std::transform(ans.m_digits.cbegin(), ans.m_digits.cend(),
                   this->m_digits.cbegin(), ans.begin(), std::plus<>{});
    return ans;
  }

  PolyType poly() const { return m_poly; }
  std::vector<long> digits() const { return m_digits; }

 private:
  PolyType m_poly;
  std::vector<long> m_digits;
};

template <>
class Coder<BalancedParams> {
 public:
  Coder() = delete;
  explicit Coder(const BalancedParams& params) : m_params(params) {}

  BalancedEncodedPoly<SparsePoly> encode(const double num) const {
    const auto [a, frac_exp] = EncodeHelper(num);
    return BalancedEncodedPoly{laurentEncode(a, frac_exp), {frac_exp}};
  }

  double decode(const BalancedEncodedPoly<SparsePoly>& en) const {
    const auto& poly = en.poly();
    auto laurentDecode = [this, i = en.digit()](double init, const auto& pair) {
      return init + pair.second * std::pow(this->m_params.rw, pair.first + i);
    };

    return std::accumulate(poly.begin(), poly.end(), 0.0, laurentDecode);
  }

 private:
  // TODO Refactor this a common code
  std::pair<SparsePoly, long> EncodeHelper(double num) const {
    const auto [rw, epsil] = m_params;
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

  SparsePoly laurentEncode(const SparsePoly& sparse_poly, long i) const {
    SparsePoly poly_map;
    for (const auto& [key, value] : sparse_poly) {
      poly_map[key - i] = value;
    }
    return poly_map;
  }

  BalancedParams m_params;
};

}  // namespace hekit::coder
