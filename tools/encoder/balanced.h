// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <algorithm>
#include <functional>
#include <vector>

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
  BalancedEncodedPoly operator+(const BalancedEncodedPoly& other) {
    auto ans = other;
    if (this->m_digits < other.m_digits) {
      ans.m_poly =
          this->m_poly + shift(other.m_poly, other.m_digits - this->m_digits);
      ans.m_digit = this->m_digit;
    } else {
      ans.m_poly =
          other.m_poly + shift(this->m_poly, this->m_digits - other.m_digits);
    }
    return ans;
  }

  BalancedEncodedPoly operator*(const BalancedEncodedPoly& other) {
    auto ans = other;
    ans.m_poly = this->m_poly * other.m_poly;
    ans.m_digit = this->m_digit + other.m_digit;
    return ans;
  }

 private:
  PolyType m_poly;
  long m_digit;
};

template <typename PolyType>
class BalancedSlotsEncodedPoly {
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

 private:
  PolyType m_poly;
  std::vector<long> m_digits;
};

template <typename PolyType>
class FractionalEncodedPoly {
 public:
  FractionalEncodedPoly operator+(const FractionalEncodedPoly& other) override {
    throw std::logic_error("Not impl.");
  }

  FractionalEncodedPoly operator*(const FractionalEncodedPoly& other) override {
    throw std::logic_error("Not impl.");
  }

 private:
  Poly m_poly;
};

}  // namespace hekit::coder
