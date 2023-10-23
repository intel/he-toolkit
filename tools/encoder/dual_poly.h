// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once
// NOTE the idea is that DualPoly wraps two EncodedPolys
// So decomp of the encoded num happens at the beginning of the logic flow

// encrypt
// Dual BalancedSlots<SparseMultiPoly> -> Dual BalancedSlots<TXT>
// Dual BalancedSlots<SparseMultiPoly> -> Dual BalancedSlots<TXT>

namespace hekit::coder {

template <typename EncodedPoly>
class DualPoly {
 public:
  DualPoly(const EncodedPoly& left, const EncodedPoly& right)
      : m_hi(left), m_lo(right) {}

  template <typename RPoly>
  DualPoly operator*(const DualPoly<RPoly>& other) const {
    const auto [other_hi, other_lo] = other.polys();
    return DualPoly(m_hi * other_hi, m_lo * other_lo);
  }

  template <typename RPoly>
  DualPoly operator*(const DualPoly<RPoly>& other) const {
    const auto [other_hi, other_lo] = other.polys();
    return DualPoly(m_hi + other_hi, m_lo + other_lo);
  }

  DualPoly& negate() {
    m_hi.negate();
    m_lo.negate();
    return *this;
  }

  DualPoly operator-() const { return DualPoly(-m_hi, -m_lo); }

  auto polys() const { return std::pair{m_hi, m_lo}; }

 private:
  EncodedPoly m_hi;
  EncodedPoly m_lo;
};

}  // namespace hekit::coder
