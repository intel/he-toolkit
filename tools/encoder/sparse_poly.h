// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <algorithm>
#include <functional>
#include <iterator>
#include <map>
#include <numeric>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include <NTL/ZZ.h>

#include "rns.h"

namespace hekit::coder {

class SparsePoly {
 public:
  SparsePoly() = default;
  explicit SparsePoly(const std::map<long, long>& terms) : m_coeffs(terms) {}
  explicit SparsePoly(const std::vector<long>& expanded_poly) {
    for (long k = 0; k < expanded_poly.size(); ++k) {
      const long v = expanded_poly[k];
      if (v != 0L) m_coeffs[k] = v;
    }
  }
  long coeff(long i) const { return m_coeffs.count(i) ? m_coeffs.at(i) : 0L; }
  void coeff(long i, long value) { m_coeffs[i] = value; }
  long degree() const {
    return m_coeffs.empty() ? 0L : m_coeffs.rbegin()->first;
  }
  long operator[](long i) const { return coeff(i); }
  long& operator[](long i) { return m_coeffs[i]; }

  SparsePoly operator+(const SparsePoly& other) const {
    auto res = other;
    for (const auto& [index, value] : m_coeffs) {
      res.m_coeffs[index] += value;
    }
    return res;
  }

  SparsePoly operator*(const SparsePoly& other) const {
    SparsePoly res{};
    for (const auto& [index1, coeff1] : m_coeffs)
      for (const auto& [index2, coeff2] : other.m_coeffs) {
        res[index1 + index2] += coeff1 * coeff2;
      }
    return res;
  }

  auto begin() noexcept { return m_coeffs.begin(); }
  const auto begin() const noexcept { return m_coeffs.begin(); }
  auto end() noexcept { return m_coeffs.end(); }
  const auto end() const noexcept { return m_coeffs.end(); }
  auto cbegin() const noexcept { return m_coeffs.cbegin(); }
  auto cend() const noexcept { return m_coeffs.cend(); }
  size_t size() const { return m_coeffs.size(); }

  auto minMaxCoeffs() const {
    return std::minmax_element(
        m_coeffs.cbegin(), m_coeffs.cend(),
        [](const auto& a, const auto& b) { return a.second < b.second; });
  }

  std::string toString() const {
    std::ostringstream oss;
    for (const auto& [key, value] : m_coeffs) {
      oss << value << "x^" << key << ((key - degree()) ? " + " : "");
    }
    return oss.str();
  }

  std::vector<long> expand() const {
    if (is_laurent())
      throw std::logic_error("Cannot expand a laurent polynomial");

    std::vector<long> expanded(degree() + 1, 0L);
    for (const auto [k, v] : m_coeffs) {
      expanded[k] = v;
    }

    return expanded;
  }

  bool is_laurent() const {
    return std::any_of(m_coeffs.cbegin(), m_coeffs.cend(),
                       [](const auto& kv) { return kv.first < 0L; });
  }

  bool operator==(const SparsePoly& other) const {
    return m_coeffs == other.m_coeffs;
  }

  SparsePoly& negate() {
    for (auto [k, v] : m_coeffs) m_coeffs[k] = -v;
    return *this;
  }

  SparsePoly& mod(long p) {
    for (auto [k, v] : m_coeffs) m_coeffs[k] = v % p;
    return *this;
  }

  using SparsePolyMod = std::pair<SparsePoly, long>;
  // NOTE Assumptions are that inside a DualPoly these Polys will have same
  // sizes and same coeffs due to all ops being applied to both indside the
  // DualPoly. Maybe we should have further sanity checks (or rethink some of
  // the design).
  static SparsePoly recompCRT(const SparsePolyMod& am,
                              const SparsePolyMod& bn) {
    const auto [a_poly, m] = am;
    const auto [b_poly, n] = bn;
    SparsePoly recomp;
    for (const auto [k, v] : a_poly) {
      recomp[k] = hekit::coder::recompCRT({v, m}, {b_poly[k], n});
    }
    return recomp;
  }

 private:
  // <index, coeff>
  std::map<long, long> m_coeffs;
};

inline SparsePoly shift(const SparsePoly& poly, long i) {
  SparsePoly tem{};
  for (const auto& [index, value] : poly) {
    tem[index + i] = value;
  }
  return tem;
}

class SparseMultiPoly {
 public:
  SparseMultiPoly() = default;
  explicit SparseMultiPoly(const std::vector<SparsePoly>& polys_in_slots)
      : m_slots(polys_in_slots) {}

  const auto& slots() const { return m_slots; }
  auto& slots() { return m_slots; }

  SparseMultiPoly operator+(const SparseMultiPoly& other) const {
    std::vector<SparsePoly> res{};
    res.reserve(m_slots.size());
    std::transform(m_slots.cbegin(), m_slots.cend(), other.m_slots.cbegin(),
                   std::back_inserter(res), std::plus<SparsePoly>{});
    return SparseMultiPoly{res};
  }

  SparseMultiPoly operator*(const SparseMultiPoly& other) const {
    std::vector<SparsePoly> res{};
    res.reserve(m_slots.size());
    std::transform(m_slots.cbegin(), m_slots.cend(), other.m_slots.cbegin(),
                   std::back_inserter(res), std::multiplies<SparsePoly>{});
    return SparseMultiPoly{res};
  }

  std::string toString() const {
    std::ostringstream oss;
    for (const auto& slot : m_slots) {
      oss << slot.toString() << '\n';
    }
    return oss.str();
  }

  bool operator==(const SparseMultiPoly& other) const {
    return m_slots == other.m_slots;
  }

  SparseMultiPoly& negate() {
    for (auto& slot : m_slots) slot.negate();
    return *this;
  }

  SparseMultiPoly& mod(long p) {
    for (auto& slot : m_slots) slot.mod(p);
    return *this;
  }

 private:
  std::vector<SparsePoly> m_slots;

  // static method
 public:
  using SparseMultiPolyMod = std::pair<SparseMultiPoly, long>;
  // NOTE Assumptions are that inside a DualPoly these Polys will have same
  // sizes and same coeffs due to all ops b eing applied to both indside the
  // DualPoly. Maybe we should have further sanity checks (or rethink some of
  // the design).
  static SparseMultiPoly recompCRT(const SparseMultiPolyMod& am,
                                   const SparseMultiPolyMod& bn) {
    const auto [a_poly, m] = am;
    const auto [b_poly, n] = bn;
    const auto a_slots = a_poly.slots();
    const auto b_slots = b_poly.slots();
    std::vector<SparsePoly> recomp;
    recomp.reserve(a_slots.size());
    for (long i = 0; i < a_slots.size(); ++i) {
      recomp.push_back(SparsePoly::recompCRT({a_slots[i], m}, {b_slots[i], n}));
    }
    return SparseMultiPoly{recomp};
  }
};

inline SparseMultiPoly shift(const SparseMultiPoly& poly,
                             const std::vector<long>& is) {
  std::vector<SparsePoly> tem{};
  tem.reserve(is.size());
  const auto slots = poly.slots();
  for (long i = 0; i < is.size(); ++i) {
    tem.push_back(shift(slots[i], is[i]));
  }
  return SparseMultiPoly{tem};
}

inline auto select(const SparseMultiPoly& lpoly, const SparseMultiPoly& rpoly,
                   const std::vector<long>& select_mask) {
  // Given a mask for the slots output selected poly and its complimentary poly
  std::vector<SparsePoly> selected;
  selected.reserve(select_mask.size());
  std::vector<SparsePoly> complimentary;
  complimentary.reserve(select_mask.size());
  const auto lslots = lpoly.slots();
  const auto rslots = rpoly.slots();
  for (long i = 0; i < select_mask.size(); ++i) {
    selected.push_back(select_mask[i] ? lslots[i] : rslots[i]);
    complimentary.push_back(select_mask[i] ? rslots[i] : lslots[i]);
  }

  return std::pair{SparseMultiPoly{selected}, SparseMultiPoly{complimentary}};
}

}  // namespace hekit::coder
