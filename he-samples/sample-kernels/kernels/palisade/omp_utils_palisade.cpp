// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "omp_utils_palisade.h"

#include <omp.h>

namespace intel {
namespace he {
namespace palisade {

const int OMPUtilitiesP::MaxThreads = omp_get_max_threads();

}  // namespace palisade
}  // namespace he
}  // namespace intel
