// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

namespace Coder {
class PolyRep {};

struct Coder {
  virtual PolyRep encode(double num) const = 0;
  virtual double decode(const PolyRep& poly_rep) const = 0;
  virtual ~Coder() = default;
};

}  // namespace Coder
