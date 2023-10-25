// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once
// NOTE the idea is that DualPoly wraps two EncodedPolys
// So decomp of the encoded num happens at the beginning of the logic flow

// encrypt
// Dual BalancedSlots<SparseMultiPoly> -> Dual BalancedSlots<TXT>
// Dual BalancedSlots<SparseMultiPoly> -> Dual BalancedSlots<TXT>

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
  DualCoder() = delete;
  explicit DualCoder(const EncodedPolyParams& params,
                     std::pair<long, long> mods)
      : m_coder(params), m_mods(mods) {}

  auto params() const { return m_coder.params(); }

  // NOTE for now just support multi nums
  auto encode(const std::vector<double>& nums) const {
    std::vector<double> hi_nums;
    hi_nums.reserve(nums.size());
    std::vector<double> lo_nums;
    lo_nums.reserve(nums.size());
    for (const auto& num : nums) {
      auto [hi_num, lo_num] = decompCRT(num, m_mods);
      hi_nums.push_back(hi_num);
      lo_nums.push_back(lo_num);
    }

    return DualPoly{m_coder.encode(hi_nums), m_coder.encode(lo_nums)};
  }

  // NOTE for now just support multi nums
  auto decode(const DualPoly<typename Coder<EncodedPolyParams>::PolyType>&
                  dual_poly) const -> std::vector<double> {
    const auto [hi_poly, lo_poly] = dual_poly.polys();
    const auto hi_nums = m_coder.decode(hi_poly);
    const auto lo_nums = m_coder.decode(lo_poly);
    auto [hi_mod, lo_mod] = m_mods;
    std::vector<double> recomposed_nums;
    recomposed_nums.reserve(hi_nums.size());
    for (long i = 0; i < hi_nums.size(); ++i) {
      recomposed_nums.push_back(
          recompCRT({hi_nums[i], hi_mod}, {lo_nums[i], lo_mod}));
    }
    return recomposed_nums;
  }

 private:
  Coder<EncodedPolyParams> m_coder;
  std::pair<long, long> m_mods;
};

}  // namespace hekit::coder
