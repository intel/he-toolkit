// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <map>

namespace hekit::poly {

class SparsePoly {
 public:
  long coeff(long i) const { return coeffs_.count(i) ? coeffs_.at(i) : 0L; }
  void coeff(long i, long value) { coeffs_[i] = value; }
  long degree() const { return coeffs_.empty() ? 0L : coeffs_.rbegin()->first; }
  long operator[](long i) const { return coeff(i); }
  long& operator[](long i) { return coeffs_[i]; }
  SparsePoly operator+(const SparsePoly& other) const {
    auto res = other;
    for (const auto& [index, value] : coeffs_) {
      res.coeffs_[index] += value;
    }
    return res;
  }
  auto begin() noexcept { return coeffs_.begin(); }
  const auto begin() const noexcept { return coeffs_.begin(); }
  auto end() noexcept { return coeffs_.end(); }
  const auto end() const noexcept { return coeffs_.end(); }
  auto cbegin() const noexcept { return coeffs_.cbegin(); }
  auto cend() const noexcept { return coeffs_.cend(); }

  void print_out_results() {
    for (const auto& [key, value] : coeffs_) {
      std::cout << "(" << key << " , " << value << ")\n";
    }
  }

  void print_poly_rep() {
    for (const auto& [key, value] : coeffs_) {
      std::cout << value << "x^" << key - mi << ((key - mi != de) ? " + " : "");
    }
  }

  // The polynomial representation for fractional decoding, where a power of 2
  // cyclotomic is used x^-i is replaced by -x^(N-i), where N is the degree of
  // the cyclotomic.
  void print_poly_rep_frac(int N) {
    for (const auto& [key, value] : coeffs_) {
      if (key < 0)
        std::cout << (-1 * value) << "x^" << N + key;
      else
        std::cout << value << "x^" << key;

      if (key != coeffs_.rbegin()->first) std::cout << " + ";
    }
  }

 private:
  // indices and coeff
  std::map<long, long> coeffs_;
};

}  // namespace hekit::poly
