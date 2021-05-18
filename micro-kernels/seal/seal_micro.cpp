// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <seal/seal.h>
#include <seal/util/ntt.h>

#include <vector>

#include "micro_util.h"
#include "seal/seal_ckks_context.h"

namespace intel {
namespace he {
namespace heseal {

void BM_Seal_InvNTT(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(3, 50), 1UL << 40,
                          false, false);

  auto parms_id = context.context()->first_parms_id();

  auto context_data_ptr = context.context()->get_context_data(parms_id);
  auto& context_data = *context_data_ptr;
  const auto& small_ntt_tables = context_data.small_ntt_tables();

  std::vector<double> input{0.0, 1.1, 2.2, 3.3};

  seal::Plaintext plain;
  seal::Ciphertext cipher;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher);

  for (auto _ : state) {
    seal::util::inverse_ntt_negacyclic_harvey(cipher.data(),
                                              small_ntt_tables[0]);
  }
}

BENCHMARK(BM_Seal_InvNTT)
    ->Unit(benchmark::kMicrosecond)
    ->Arg(512)
    ->Arg(1024)
    ->Arg(2048)
    ->Arg(4096)
    ->Arg(8192)
    ->Arg(16384);
//=================================================================

void BM_Seal_FwdNTT(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(3, 50), 1UL << 40,
                          false, false);

  auto parms_id = context.context()->first_parms_id();

  auto context_data_ptr = context.context()->get_context_data(parms_id);
  auto& context_data = *context_data_ptr;
  const auto& small_ntt_tables = context_data.small_ntt_tables();

  std::vector<double> input{0.0, 1.1, 2.2, 3.3};

  seal::Plaintext plain;
  seal::Ciphertext cipher;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher);

  for (auto _ : state) {
    seal::util::ntt_negacyclic_harvey(cipher.data(), small_ntt_tables[0]);
  }
}

BENCHMARK(BM_Seal_FwdNTT)
    ->Unit(benchmark::kMicrosecond)
    ->Arg(512)
    ->Arg(1024)
    ->Arg(2048)
    ->Arg(4096)
    ->Arg(8192)
    ->Arg(16384);

//=================================================================

}  // namespace heseal
}  // namespace he
}  // namespace intel
