// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once
// NOTE the idea is that NPoly wraps two EncodedPolys
// So decomp of the encoded num happens at the beginning of the logic flow

// encrypt
// N BalancedSlots<SparseMultiPoly> -> N BalancedSlots<TXT>
// N BalancedSlots<SparseMultiPoly> -> N BalancedSlots<TXT>

#include <type_traits>
#include <vector>

#include "rns.h"

namespace hekit::coder {

template <typename EncodedPoly>
class NPoly {
 public:
  explicit NPoly(const std::vector<EncodedPoly>& polys) : m_polys(polys) {}

  template <typename RPoly>
  NPoly operator*(const NPoly<RPoly>& other) const {
    const auto polys = other.polys();
    std::vector<EncodedPoly> ans;
    ans.reserve(m_polys.size());
    for (long i = 0; i < m_polys.size(); ++i)
      ans.emplace_back(m_polys[i] * polys[i]);
    return NPoly(ans);
  }

  template <typename RPoly>
  NPoly operator+(const NPoly<RPoly>& other) const {
    const auto polys = other.polys();
    std::vector<EncodedPoly> ans;
    ans.reserve(m_polys.size());
    for (long i = 0; i < m_polys.size(); ++i)
      ans.emplace_back(m_polys[i] + polys[i]);
    return NPoly(ans);
  }

  NPoly& negate() {
    for (auto& poly : m_polys) poly.negate();
    return *this;
  }

  NPoly operator-() const {
    auto ans = *this;
    return ans.negate();
  }

  // Shift poly by x coeffs values not modded
  NPoly shiftRepresentation() const {
    std::vector<EncodedPoly> polys;
    polys.reserve(m_polys.size());
    std::transform(m_polys.cbegin(), m_polys.cend(), std::back_inserter(polys),
                   [](auto poly) { return poly.shiftRepresentation(); });
    return NPoly{polys};
  }

  auto polys() const { return m_polys; }

  auto size() const { return m_polys.size(); }

 private:
  std::vector<EncodedPoly> m_polys;
  std::vector<long> m_mods;
};

// NOTE the dual coder for now is its own class and not a Coder
// specialization
template <typename EncodedPolyParams>
class NCoder {
 public:
  // e.g. BalancedSlotsEncodedPoly, etc
  using CoderPolyType = typename Coder<EncodedPolyParams>::PolyType;

  NCoder() = delete;
  explicit NCoder(const EncodedPolyParams& params, std::vector<long> mods)
      : m_coder(params), m_mods(mods) {}

  auto params() const { return m_coder.params(); }

  // Input i.e. double or vector of doubles
  template <typename Input>
  auto encode(const Input& num) const {
    const auto whole_encoded = m_coder.encode(num);
    std::vector<CoderPolyType> polys;
    polys.reserve(m_mods.size());
    for (long i = 0; i < m_mods.size(); ++i)
      polys.emplace_back(mod<Input>(whole_encoded, m_mods[i]));
    return NPoly<CoderPolyType>(polys);
  }

  auto decode(const NPoly<CoderPolyType>& npoly) const {
    return m_coder.decode(recompose(npoly));
  }

 private:
  Coder<EncodedPolyParams> m_coder;
  std::vector<long> m_mods;

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
  auto recompose(const NPoly<CoderPolyType>& npoly) const
      -> decltype(CoderPolyType{Q{}, 0L}) {
    const auto encoded_polys = npoly.polys();
    if (std::any_of(
            encoded_polys.begin(), encoded_polys.end(),
            [first_digit = encoded_polys.front().digit()](const auto& poly) {
              return poly.digit() != first_digit;
            }))
      throw std::logic_error("Digits were not equal while recomposing");

    // NOTE logic could be simplified if NPoly carried the mods info
    auto recomposed_poly = encoded_polys.front().poly();
    auto recomposed_mod = m_mods.front();
    for (long i = 1; i < m_mods.size(); ++i) {
      std::cout << "recomp loop\n";
      recomposed_poly = CoderPolyType::UsingPolyType::recompCRT(
          std::pair{recomposed_poly, recomposed_mod},
          std::pair{encoded_polys[i].poly(), m_mods[i]});
      recomposed_mod *= m_mods[i];
    }

    return CoderPolyType{recomposed_poly, encoded_polys.front().digit()};
  }

  // Multi nums encoding
  //  template <typename Q = typename CoderPolyType::UsingPolyType>
  //  auto recompose(const NPoly<CoderPolyType>& npoly) const
  //      -> decltype(CoderPolyType{Q{}, std::vector<long>{}}) {
  //    const auto encoded_polys = npoly.polys();
  //    if (std::any_of(encoded_polys.begin(), encoded_polys.end(),
  //      [first_digits = encoded_polys.front().digits()] (const auto& digits) {
  ///        return digits != first_digits;
  //        }))
  //        throw std::logic_error("Digits were not equal while recomposing");
  //
  //    // TODO for multivalues (slots)
  //    const auto [m, n] = m_mods;
  //    const auto recomposed_poly = CoderPolyType::UsingPolyType::recompCRT(
  //        {hi_encoded.poly(), m}, {lo_encoded.poly(), n});
  //    return CoderPolyType{recomposed_poly, hi_encoded.digits()};
  //  }
};

}  // namespace hekit::coder
