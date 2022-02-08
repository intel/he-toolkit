// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include "kernels/omp_utils.h"

namespace intel {
namespace he {
namespace palisade {

class OMPUtilitiesP : public OMPUtilities {
 public:
  static const int MaxThreads;
};

}  // namespace palisade
}  // namespace he
}  // namespace intel
