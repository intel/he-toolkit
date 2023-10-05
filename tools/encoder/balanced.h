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
 public:
  BalancedSlotsEncodedPoly() = delete;
  BalancedSlotsEncodedPoly(const PolyType& poly,
                           const std::vector<long>& digits)
      : m_poly(poly), m_digits(digits) {}

  BalancedSlotsEncodedPoly operator+(
      const BalancedSlotsEncodedPoly& other) const {
    std::vector<long> select_digits;
    select_digits.reserve(m_digits.size());
    std::transform(
        m_digits.cbegin(), m_digits.cend(), other.m_digits.cbegin(),
        std::back_inserter(select_digits),
        [](const long lhs, const long rhs) { return std::min(lhs, rhs); });

    std::vector<long> select_mask;
    select_mask.reserve(m_digits.size());
    std::transform(m_digits.cbegin(), m_digits.cend(), other.m_digits.cbegin(),
                   std::back_inserter(select_mask), std::less<long>{});

    std::vector<long> shift_digits;
    shift_digits.reserve(m_digits.size());
    std::transform(m_digits.cbegin(), m_digits.cend(), other.m_digits.cbegin(),
                   std::back_inserter(shift_digits),
                   [](const auto& ldigit, const auto& rdigit) {
                     return (ldigit < rdigit) ? rdigit - ldigit
                                              : ldigit - rdigit;
                   });

    const auto [select_poly, complimentary_poly] =
        select(m_poly, other.m_poly, select_mask);

    return BalancedSlotsEncodedPoly<PolyType>{
        select_poly + shift(complimentary_poly, shift_digits), select_digits};

    // if (this->m_digit < other.m_digit) {
    //{
    //   ans.m_poly = this->m_poly + shift(other.m_poly, other.m_digits -
    //   this->m_digits);
    // } else {
    //   ans.m_poly = other.m_poly + shift(this->m_poly, this->m_digits -
    //   other.m_digits);
    // }
  }

  BalancedSlotsEncodedPoly operator*(
      const BalancedSlotsEncodedPoly& other) const {
    auto ans = *this;
    ans.m_poly = this->m_poly * other.m_poly;
    std::transform(other.m_digits.cbegin(), other.m_digits.cend(),
                   m_digits.cbegin(), ans.m_digits.begin(), std::plus<>{});
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

  auto params() const { return m_params; }

  BalancedEncodedPoly<SparsePoly> encode(const double num) const {
    const auto [a, frac_exp] = EncodeHelper(num);
    return BalancedEncodedPoly{laurentEncode(a, frac_exp), {frac_exp}};
  }

  double decode(const BalancedEncodedPoly<SparsePoly>& en) const {
    const auto& poly = en.poly();
    auto laurentDecode = [rw = m_params.rw, i = en.digit()](double init,
                                                            const auto& pair) {
      return init + pair.second * std::pow(rw, pair.first + i);
    };

    return std::accumulate(poly.begin(), poly.end(), 0.0, laurentDecode);
  }

 private:
  // TODO Refactor this a common code
  std::pair<SparsePoly, long> EncodeHelper(double num) const {
    const auto [rw, epsil] = m_params;
    const double log_rw = std::log(rw);
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

template <>
class Coder<BalancedSlotsParams> {
 public:
  Coder() = delete;
  explicit Coder(const BalancedSlotsParams& params) : m_params(params) {}

  BalancedSlotsEncodedPoly<SparseMultiPoly> encode(
      const std::vector<double>& nums) const {
    std::vector<SparsePoly> polys;
    std::vector<long> is;
    for (double num : nums) {
      const auto [a, frac_exp] = EncodeHelper(num);
      polys.push_back(laurentEncode(a, frac_exp));
      is.push_back(frac_exp);
    }
    return BalancedSlotsEncodedPoly{SparseMultiPoly{polys}, is};
  }

  std::vector<double> decode(
      const BalancedSlotsEncodedPoly<SparseMultiPoly>& en) const {
    const auto slots = en.poly().slots();
    if (slots.size() != en.digits().size()) {
      std::ostringstream msg;
      msg << "Slots and digits sizes do not match: " << slots.size()
          << " != " << en.digits().size();
      throw std::logic_error(msg.str());
    }
    std::vector<double> nums;
    nums.reserve(slots.size());
    for (int n = 0; n < slots.size(); ++n) {
      const auto& poly = slots[n];
      auto laurentDecode = [rw = m_params.rw, i = en.digits().at(n)](
                               double init, const auto& pair) {
        return init + pair.second * std::pow(rw, pair.first + i);
      };
      nums.emplace_back(
          std::accumulate(poly.begin(), poly.end(), 0.0, laurentDecode));
    }
    return nums;
  }

 private:
  // TODO Refactor this a common code
  std::pair<SparsePoly, long> EncodeHelper(double num) const {
    const auto [rw, epsil] = m_params;
    const double log_rw = std::log(rw);
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

  BalancedSlotsParams m_params;
};

}  // namespace hekit::coder
