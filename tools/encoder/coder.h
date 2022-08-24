// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <vector>

template <typename Poly>
class EncPoly {
 public:
  EncPoly() = delete;
  EncPoly(poly, is) : poly_(poly), is_(is) {}

 private:
  std::vector<long> is_;
  Poly poly_;
};

template <typename Poly>
struct Coder {
  virtual EncPoly<Poly> encode(double num) = 0;
  virtual double decode(const EncPoly<Poly>& enc_poly) = 0;
  virtual ~Coder = default;
};
