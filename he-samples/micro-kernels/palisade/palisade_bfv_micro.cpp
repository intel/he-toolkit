// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <palisade.h>

#include <vector>

#include "micro_util.h"
#include "palisade/palisade_util.h"

namespace intel {
namespace he {
namespace palisade {

//=================================================================
static void BM_Encode_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));

  auto keys = cc->KeyGen();
  auto input = generateVector<int64_t>(state.range(0) / 2);

  for (auto _ : state) {
    lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  }
}
HE_MICRO_BENCHMARK(BM_Encode_Palisade_BFV);

//=================================================================

static void BM_EncodeEncrypt_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);

  for (auto _ : state) {
    lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
    auto c1 = cc->Encrypt(keys.publicKey, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_EncodeEncrypt_Palisade_BFV);

//=================================================================

static void BM_Encrypt_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);

  for (auto _ : state) {
    auto c1 = cc->Encrypt(keys.publicKey, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_Encrypt_Palisade_BFV);

//=================================================================

static void BM_Decrypt_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);

  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, c1, &result);
  }
}
HE_MICRO_BENCHMARK(BM_Decrypt_Palisade_BFV);

//=================================================================

static void BM_Decode_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);

  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext result;
  cc->Decrypt(keys.secretKey, c1, &result);

  for (auto _ : state) {
    result->Decode();
  }
}
HE_MICRO_BENCHMARK(BM_Decode_Palisade_BFV);

//=================================================================

static void BM_DecryptDecode_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);

  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, c1, &result);

    result->Decode();
  }
}
HE_MICRO_BENCHMARK(BM_DecryptDecode_Palisade_BFV);

//=================================================================

static void BM_Add_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);

  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakePackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalAdd(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_Add_Palisade_BFV);

//=================================================================

static void BM_Sub_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakePackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalSub(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_Sub_Palisade_BFV);

//=================================================================

static void BM_AddPlain_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalAdd(c1, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_AddPlain_Palisade_BFV);

//=================================================================

static void BM_SubPlain_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalSub(c1, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_SubPlain_Palisade_BFV);

//=================================================================

static void BM_Negate_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalNegate(c1);
  }
}
HE_MICRO_BENCHMARK(BM_Negate_Palisade_BFV);

//=================================================================

static void BM_Multiply_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakePackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalMultNoRelin(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_Multiply_Palisade_BFV);

//=================================================================

static void BM_MultiplyRelin_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakePackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalMultAndRelinearize(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyRelin_Palisade_BFV);

//=================================================================
static void BM_Square_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakePackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalMultNoRelin(c1, c1);
  }
}
HE_MICRO_BENCHMARK(BM_Square_Palisade_BFV);

//=================================================================

static void BM_MultiplyPlain_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalMult(c1, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyPlain_Palisade_BFV);

//=================================================================

static void BM_Rotate1_Palisade_BFV(benchmark::State& state) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, {1, -2, 2, 3, 4, 5, 6, 7, 8, 9});

  auto input = generateVector<int64_t>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakePackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalAtIndex(c1, 1);
  }
}
HE_MICRO_BENCHMARK(BM_Rotate1_Palisade_BFV);

//=================================================================

}  // namespace palisade
}  // namespace he
}  // namespace intel
