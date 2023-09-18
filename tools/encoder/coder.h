// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

namespace hekit::coder {

// specialisations are kept in the appropriate scheme files
template <typename Scheme>
class Coder {
  // Specialisations only
  static_assert(!std::is_same<Scheme, Scheme>(),
                "Only allowed schemes can be used");
  // Pointless ctor is required for CTAD
  explicit Coder(const Scheme& params) {}
};

// TODO move to more appropriate header?
inline constexpr double signum(double x) { return (x > 0.0) - (x < 0.0); }

}  // namespace hekit::coder
