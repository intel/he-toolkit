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
  using UsingPolyType = PolyType;

  BalancedEncodedPoly() = delete;
  BalancedEncodedPoly(const PolyType& poly, long digit)
      : m_poly(poly), m_digit(digit) {}

  template <typename RPOLY>
  BalancedEncodedPoly operator+(const BalancedEncodedPoly<RPOLY>& other) const {
    auto ans = *this;
    if (this->m_digit < other.digit()) {
      ans.m_poly =
          this->m_poly + shift(other.poly(), other.digit() - this->m_digit);
    } else {
      ans.m_poly =
          shift(this->m_poly, this->m_digit - other.digit()) + other.poly();
      ans.m_digit = other.digit();
    }
    return ans;
  }

  template <typename RPOLY>
  BalancedEncodedPoly operator*(const BalancedEncodedPoly<RPOLY>& other) const {
    auto ans = *this;
    ans.m_poly = this->m_poly * other.poly();
    ans.m_digit = this->m_digit + other.digit();
    return ans;
  }

  PolyType poly() const { return m_poly; }
  long digit() const { return m_digit; }

  BalancedEncodedPoly& negate() {
    m_poly.negate();
    return *this;
  }

  BalancedEncodedPoly operator-() const {
    auto ans = *this;
    return ans.negate();
  }

  BalancedEncodedPoly shiftRepresentation(long i = 1L) const {
    return BalancedEncodedPoly{shift(m_poly, i), m_digit - i};
  }

 private:
  PolyType m_poly;
  long m_digit;
};

template <typename PolyType>
class BalancedSlotsEncodedPoly {
 public:
  using UsingPolyType = PolyType;

  BalancedSlotsEncodedPoly() = delete;
  BalancedSlotsEncodedPoly(const PolyType& poly,
                           const std::vector<long>& digits)
      : m_poly(poly), m_digits(digits) {}

  template <typename RPOLY>
  BalancedSlotsEncodedPoly operator+(
      const BalancedSlotsEncodedPoly<RPOLY>& other) const {
    std::vector<long> select_digits;
    select_digits.reserve(m_digits.size());
    std::transform(
        m_digits.cbegin(), m_digits.cend(), other.digits().cbegin(),
        std::back_inserter(select_digits),
        [](const long lhs, const long rhs) { return std::min(lhs, rhs); });

    std::vector<long> select_mask;
    select_mask.reserve(m_digits.size());
    std::transform(m_digits.cbegin(), m_digits.cend(), other.digits().cbegin(),
                   std::back_inserter(select_mask), std::less<long>{});

    std::vector<long> shift_digits;
    shift_digits.reserve(m_digits.size());
    std::transform(m_digits.cbegin(), m_digits.cend(), other.digits().cbegin(),
                   std::back_inserter(shift_digits),
                   [](const auto& ldigit, const auto& rdigit) {
                     return (ldigit < rdigit) ? rdigit - ldigit
                                              : ldigit - rdigit;
                   });

    const auto [select_poly, complimentary_poly] =
        select(m_poly, other.poly(), select_mask);

    return BalancedSlotsEncodedPoly{
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

  template <typename RPOLY>
  BalancedSlotsEncodedPoly operator*(
      const BalancedSlotsEncodedPoly<RPOLY>& other) const {
    const auto poly = this->m_poly * other.poly();
    auto other_digits = other.digits();
    decltype(other_digits) digits;
    digits.reserve(other_digits.size());
    std::transform(other_digits.cbegin(), other_digits.cend(),
                   m_digits.cbegin(), std::back_inserter(digits),
                   std::plus<>{});
    return BalancedSlotsEncodedPoly{poly, digits};
  }

  PolyType poly() const { return m_poly; }
  std::vector<long> digits() const { return m_digits; }

  BalancedSlotsEncodedPoly& negate() {
    m_poly.negate();
    return *this;
  }

  BalancedSlotsEncodedPoly operator-() const {
    auto ans = *this;
    return ans.negate();
  }

 private:
  PolyType m_poly;
  std::vector<long> m_digits;
};

template <>
class Coder<BalancedParams> {
 public:
  using PolyType = BalancedEncodedPoly<SparsePoly>;

  Coder() = delete;
  explicit Coder(const BalancedParams& params) : m_params(params) {}

  auto params() const { return m_params; }

  BalancedEncodedPoly<SparsePoly> encode(const double num) const {
    const auto [rw, epsil] = m_params;
    const auto a_poly = encodeNumToLaurent(num, rw, epsil);
    const auto frac_exp = computeFracExp(a_poly);
    return BalancedEncodedPoly{encodeLaurentToBalanced(a_poly, frac_exp),
                               {frac_exp}};
  }

  double decode(const BalancedEncodedPoly<SparsePoly>& en) const {
    const auto& poly = en.poly();
    auto laurentDecode = [rw = m_params.rw, i = en.digit()](NTL::RR init,
                                                            const auto& pair) {
      const auto coeff = NTL::conv<NTL::RR>(pair.second);
      return init + coeff * std::pow(rw, pair.first + i);
    };

    const auto result_RR =
        std::accumulate(poly.begin(), poly.end(), NTL::RR(0.0), laurentDecode);
    double result = NTL::conv<double>(result_RR);
    return result;
  }

 private:
  SparsePoly encodeLaurentToBalanced(const SparsePoly& sparse_poly,
                                     long i) const {
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
  using PolyType = BalancedSlotsEncodedPoly<SparseMultiPoly>;

  Coder() = delete;
  explicit Coder(const BalancedSlotsParams& params) : m_params(params) {}

  auto params() const { return m_params; }

  BalancedSlotsEncodedPoly<SparseMultiPoly> encode(
      const std::vector<double>& nums) const {
    std::vector<SparsePoly> polys;
    polys.reserve(nums.size());
    std::vector<long> is;
    const auto [rw, epsil] = m_params;
    for (double num : nums) {
      const auto a_poly = encodeNumToLaurent(num, rw, epsil);
      const auto frac_exp = computeFracExp(a_poly);
      polys.push_back(encodeLaurentToBalanced(a_poly, frac_exp));
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
                               NTL::RR init, const auto& pair) {
        const auto coeff = NTL::conv<NTL::RR>(pair.second);
        return init + coeff * std::pow(rw, pair.first + i);
      };
      nums.emplace_back(NTL::conv<double>(std::accumulate(
          poly.begin(), poly.end(), NTL::RR(0.0), laurentDecode)));
    }
    return nums;
  }

 private:
  SparsePoly encodeLaurentToBalanced(const SparsePoly& sparse_poly,
                                     long i) const {
    SparsePoly poly_map;
    for (const auto& [key, value] : sparse_poly) {
      poly_map[key - i] = value;
    }
    return poly_map;
  }

  BalancedSlotsParams m_params;
};

}  // namespace hekit::coder
