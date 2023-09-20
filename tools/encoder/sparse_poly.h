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
#include <vector>

namespace hekit::coder {

class SparsePoly {
 public:
  SparsePoly() = default;
  explicit SparsePoly(const std::map<long, long>& terms) : m_coeffs(terms) {}
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

  std::string toString() const {
    std::ostringstream oss;
    for (const auto& [key, value] : m_coeffs) {
      oss << value << "x^" << key << ((key - degree()) ? " + " : "");
    }
    return oss.str();
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

  SparsePoly poly() const {
    return std::accumulate(m_slots.begin(), m_slots.end(), SparsePoly{},
                           std::multiplies<SparsePoly>{});
  }

  auto slots() const { return m_slots; }

  SparseMultiPoly operator+(const SparseMultiPoly& other) const {
    std::vector<SparsePoly> res{};
    res.reserve(m_slots.size());
    std::transform(m_slots.begin(), m_slots.end(), other.m_slots.begin(),
                   std::back_inserter(res), std::plus<SparsePoly>{});
    return SparseMultiPoly{res};
  }

  SparseMultiPoly operator*(const SparseMultiPoly& other) const {
    std::vector<SparsePoly> res{};
    res.reserve(m_slots.size());
    std::transform(m_slots.begin(), m_slots.end(), other.m_slots.begin(),
                   std::back_inserter(res), std::multiplies<SparsePoly>{});
    return SparseMultiPoly{res};
  }

 private:
  std::vector<SparsePoly> m_slots;
};
}  // namespace hekit::coder
