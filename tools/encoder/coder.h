// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

class PolyRep;

struct Coder {
  virtual PolyRep encode(double num) = 0;
  virtual double decode(const PolyRep& poly_rep) = 0;
  virtual ~Coder = default;
};
