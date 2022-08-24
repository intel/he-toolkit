// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

// Takes in the number to encode, the base, the precision and the size of the
// array returns a list of coefficients after the shift. So the list can
// directly be turned into a polynomial.

#pragma once

#include <algorithm>
#include <cmath>
#include <iterator>
#include <map>
#include <vector>

inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

class SparsePoly {
 public:
  long coeff(long i) const { return coeffs_.count(i) ? coeffs_.at(i) : 0L; }
  void coeff(long i, long value) { coeffs_[i] = value; }
  long degree() const { return coeffs_.rbegin()->first; }
  long operator[](long i) const { return coeff(i); }
  long& operator[](long i) { return coeffs_[i]; }
  SparsePoly operator+(const SparsePoly& other) const {
    auto res = other;
    for (const auto [index, value] : coeffs_) {
      res.coeffs_[index] += value;
    }
    return res;
  }

 private:
  std::map<long, long> coeffs_;
};

class Coder {
 public:
  Coder() = default;

  Coder(double bw, double epsil) : bw_(bw), epsil_(epsil) {}

  std::map<long, long> encode(double num) {
    const double log_bw_ = std::log(bw_);
    std::map<long, long> a;
    long r;
    double t_minus_po;
    for (double t = std::abs(num), sigma = signum(num); t >= epsil_;
         t = std::abs(t_minus_po), sigma *= signum(t_minus_po)) {
      r = std::ceil(std::log(t) / log_bw_);
      r -= (std::pow(bw_, r) - t > t - std::pow(bw_, r - 1));

      a[r] = sigma;
      t_minus_po = t - std::pow(bw_, r);
    }
    return a;
  }

  template <typename T>
  void print_out_results(const T& en) {
    for (const auto& [key, value] : en) {
      std::cout << "(" << key << " , " << value << ")" << std::endl;
    }
  }

  template <typename T, typename U, typename W>
  void print_poly_rep(const T& en, U mi, W de) {
    for (const auto& [key, value] : en) {
      std::cout << value << "x^" << key - mi;
      if (key - mi != de) std::cout << " + ";
    }
  }

  // The polynomial representation for fractional decoding, where a power of 2
  // cyclcotomic is used x^-i is replaced by -x^(N-i), where N is the degree of
  // the cyclotomic.
  template <typename T>
  void print_poly_rep_frac(const T& en, int N) {
    for (const auto& [key, value] : en) {
      if (key < 0)
        std::cout << (-1) * value << "x^" << N + key;
      else
        std::cout << value << "x^" << key;

      if (key != prev(en.end())->first) std::cout << " + ";
    }
  }

  template <typename T>
  double decoder(const T& en) {
    double sum = 0;
    for (const auto& [key, value] : en) {
      sum += value * pow(bw_, key);
    }
    return sum;
  }

 private:
  double bw_ = 1.2;
  double epsil_ = 0.00000001;
};
