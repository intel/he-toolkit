// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once
// NOTE the idea is that DualPoly wraps two EncodedPolys
// So decomp of the encoded num happens at the beginning of the logic flow

// encrypt
// Dual BalancedSlots<SparseMultiPoly> -> Dual BalancedSlots<TXT>
// Dual BalancedSlots<SparseMultiPoly> -> Dual BalancedSlots<TXT>

#include <type_traits>
#include <utility>
#include <vector>

#include "rns.h"

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
  DualPoly operator+(const DualPoly<RPoly>& other) const {
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

// NOTE the dual coder for now is its own class and not a Coder
// specialization
template <typename EncodedPolyParams>
class DualCoder {
 public:
  // e.g. BalancedSlotsEncodedPoly, etc
  using CoderPolyType = typename Coder<EncodedPolyParams>::PolyType;

  DualCoder() = delete;
  explicit DualCoder(const EncodedPolyParams& params,
                     std::pair<long, long> mods)
      : m_coder(params), m_mods(mods) {}

  auto params() const { return m_coder.params(); }

  // Input i.e. double or vector of doubles
  template <typename Input>
  auto encode(const Input& num) const {
    const auto whole_encoded = m_coder.encode(num);
    return DualPoly{mod<Input>(whole_encoded, m_mods.first),
                    mod<Input>(whole_encoded, m_mods.second)};
  }

  auto decode(const DualPoly<CoderPolyType>& dual_poly) const {
    return m_coder.decode(recompose(dual_poly));
  }

 private:
  Coder<EncodedPolyParams> m_coder;
  std::pair<long, long> m_mods;

  template <typename T>
  static auto mod(const CoderPolyType& encoded_poly, long p) {
    auto poly = encoded_poly.poly().mod(p);
    if constexpr (std::is_same_v<std::vector<double>, T>)
      return CoderPolyType{poly, encoded_poly.digits()};
    else
      return CoderPolyType{poly, encoded_poly.digit()};
  }

  // Single nums encoding
  template <typename Q = typename CoderPolyType::UsingPolyType>
  auto recompose(const DualPoly<CoderPolyType>& dual_poly) const
      -> decltype(CoderPolyType{Q{}, 0L}) {
    const auto [hi_encoded, lo_encoded] = dual_poly.polys();
    if (hi_encoded.digit() != lo_encoded.digit())
      throw std::logic_error("Digits were not equal while recomposing");

    const auto [m, n] = m_mods;
    const auto recomposed_poly = CoderPolyType::UsingPolyType::recompCRT(
        {hi_encoded.poly(), m}, {lo_encoded.poly(), n});
    return CoderPolyType{recomposed_poly, hi_encoded.digit()};
  }

  // Multi nums encoding
  template <typename Q = typename CoderPolyType::UsingPolyType>
  auto recompose(const DualPoly<CoderPolyType>& dual_poly) const
      -> decltype(CoderPolyType{Q{}, std::vector<long>{}}) {
    const auto [hi_encoded, lo_encoded] = dual_poly.polys();
    if (hi_encoded.digits() != lo_encoded.digits())
      throw std::logic_error("Digits were not equal while recomposing");

    const auto [m, n] = m_mods;
    const auto recomposed_poly = CoderPolyType::UsingPolyType::recompCRT(
        {hi_encoded.poly(), m}, {lo_encoded.poly(), n});
    return CoderPolyType{recomposed_poly, hi_encoded.digits()};
  }
};

}  // namespace hekit::coder
