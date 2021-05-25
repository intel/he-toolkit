// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <palisade.h>

#include "micro_util.h"
#include "palisade/palisade_util.h"

namespace intel {
namespace he {
namespace palisade {

//=================================================================
static void BM_Palisade_FwdNTT(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0), std::vector<int>(3, 50));

  usint m = 2 * state.range(0);
  size_t phim = m / 2;

  NativeInteger modulusQ = lbcrypto::FirstPrime<NativeInteger>(45, m);
  NativeInteger rootOfUnity = RootOfUnity(m, modulusQ);

  lbcrypto::DiscreteUniformGeneratorImpl<NativeVector> dug;
  dug.SetModulus(modulusQ);
  NativeVector x = dug.GenerateVector(phim);
  NativeVector X(phim);

  lbcrypto::ChineseRemainderTransformFTT<NativeVector>::PreCompute(rootOfUnity,
                                                                   m, modulusQ);

  for (auto _ : state) {
    lbcrypto::ChineseRemainderTransformFTT<
        NativeVector>::ForwardTransformToBitReverse(x, rootOfUnity, m, &X);
  }
}
BENCHMARK(BM_Palisade_FwdNTT)
    ->Unit(benchmark::kMicrosecond)
    ->Arg(512)
    ->Arg(1024)
    ->Arg(2048)
    ->Arg(4096)
    ->Arg(8192)
    ->Arg(16384);

//=================================================================
static void BM_Palisade_InvNTT(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0), std::vector<int>(3, 50));

  usint m = 2 * state.range(0);
  size_t phim = m / 2;

  NativeInteger modulusQ = lbcrypto::FirstPrime<NativeInteger>(45, m);
  NativeInteger rootOfUnity = RootOfUnity(m, modulusQ);

  lbcrypto::DiscreteUniformGeneratorImpl<NativeVector> dug;
  dug.SetModulus(modulusQ);
  NativeVector x = dug.GenerateVector(phim);
  NativeVector X(phim);

  lbcrypto::ChineseRemainderTransformFTT<NativeVector>::PreCompute(rootOfUnity,
                                                                   m, modulusQ);

  for (auto _ : state) {
    lbcrypto::ChineseRemainderTransformFTT<
        NativeVector>::InverseTransformFromBitReverse(x, rootOfUnity, m, &X);
  }
}
BENCHMARK(BM_Palisade_InvNTT)
    ->Unit(benchmark::kMicrosecond)
    ->Arg(512)
    ->Arg(1024)
    ->Arg(2048)
    ->Arg(4096)
    ->Arg(8192)
    ->Arg(16384);

//================================================================

}  // namespace palisade
}  // namespace he
}  // namespace intel
