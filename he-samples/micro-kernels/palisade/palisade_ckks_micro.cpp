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
static void BM_Encode_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));

  auto input = generateVector<double>(state.range(0) / 2);

  for (auto _ : state) {
    lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
    ptxt1->Encode();
  }
}
HE_MICRO_BENCHMARK(BM_Encode_Palisade_CKKS);

//=================================================================

static void BM_Encrypt_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);

  for (auto _ : state) {
    auto c1 = cc->Encrypt(keys.publicKey, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_Encrypt_Palisade_CKKS);

//=================================================================

static void BM_EncodeEncrypt_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0) / 2);

  for (auto _ : state) {
    lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
    auto c1 = cc->Encrypt(keys.publicKey, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_EncodeEncrypt_Palisade_CKKS);

//=================================================================

static void BM_Decrypt_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0));

  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  c1 = cc->LevelReduce(c1, nullptr, 1);

  for (auto _ : state) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, c1, &result);
  }
}
HE_MICRO_BENCHMARK(BM_Decrypt_Palisade_CKKS);

//=================================================================

static void BM_Decode_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0));

  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext result;
  cc->Decrypt(keys.secretKey, c1, &result);

  double scaling_factor = std::pow(2, 50);
  auto ckks_result =
      std::static_pointer_cast<lbcrypto::CKKSPackedEncoding>(result);

  for (auto _ : state) {
    ckks_result->Decode(1, scaling_factor, lbcrypto::APPROXRESCALE);
  }
}
HE_MICRO_BENCHMARK(BM_Decode_Palisade_CKKS);

//=================================================================

static void BM_DecryptDecode_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0));

  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  double scaling_factor = std::pow(2, 50);

  for (auto _ : state) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, c1, &result);
    std::static_pointer_cast<lbcrypto::CKKSPackedEncoding>(result)->Decode(
        1, scaling_factor, lbcrypto::APPROXRESCALE);
  }
}
HE_MICRO_BENCHMARK(BM_DecryptDecode_Palisade_CKKS);

//=================================================================

static void BM_Add_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0) / 2);

  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakeCKKSPackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalAdd(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_Add_Palisade_CKKS);

//=================================================================

static void BM_Sub_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakeCKKSPackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalSub(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_Sub_Palisade_CKKS);

//=================================================================

static void BM_AddPlain_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  // Inputs
  std::vector<double> input;
  for (size_t i = 0; i < state.range(0); ++i) {
    input.emplace_back(static_cast<double>(i));
  }
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalAdd(c1, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_AddPlain_Palisade_CKKS);

//=================================================================

static void BM_SubPlain_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  // Inputs
  std::vector<double> input;
  for (size_t i = 0; i < state.range(0); ++i) {
    input.emplace_back(static_cast<double>(i));
  }
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalSub(c1, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_SubPlain_Palisade_CKKS);

//=================================================================

static void BM_AddPlainScalar_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  // Inputs
  std::vector<double> input;
  for (size_t i = 0; i < state.range(0); ++i) {
    input.emplace_back(static_cast<double>(i));
  }
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalAdd(c1, 1.7);
  }
}
HE_MICRO_BENCHMARK(BM_AddPlainScalar_Palisade_CKKS);

//=================================================================

static void BM_SubPlainScalar_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  // Inputs
  std::vector<double> input;
  for (size_t i = 0; i < state.range(0); ++i) {
    input.emplace_back(static_cast<double>(i));
  }
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalSub(c1, 1.7);
  }
}
HE_MICRO_BENCHMARK(BM_SubPlainScalar_Palisade_CKKS);

//=================================================================

static void BM_Negate_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalNegate(c1);
  }
}
HE_MICRO_BENCHMARK(BM_Negate_Palisade_CKKS);

//=================================================================
static void BM_Multiply_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakeCKKSPackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalMultNoRelin(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_Multiply_Palisade_CKKS);

//=================================================================

static void BM_MultiplyRelin_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakeCKKSPackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalMultAndRelinearize(c1, c2);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyRelin_Palisade_CKKS);

//=================================================================

static void BM_MultiplyRelinRescale_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakeCKKSPackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalMultAndRelinearize(c1, c2);
    c3 = cc->Rescale(c3);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyRelinRescale_Palisade_CKKS);

//=================================================================

static void BM_Square_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  lbcrypto::Plaintext ptxt2 = cc->MakeCKKSPackedPlaintext(input);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  for (auto _ : state) {
    auto c3 = cc->EvalMultNoRelin(c1, c1);
  }
}
HE_MICRO_BENCHMARK(BM_Square_Palisade_CKKS);

//=================================================================

static void BM_MultiplyPlain_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalMult(c1, ptxt1);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyPlain_Palisade_CKKS);

//=================================================================

static void BM_MultiplyPlainScalar_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalMult(c1, 1.23);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyPlainScalar_Palisade_CKKS);

//=================================================================

static void BM_Rotate1_Palisade_CKKS(benchmark::State& state) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));
  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, {1, -2});

  auto input = generateVector<double>(state.range(0) / 2);
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(input);
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);

  for (auto _ : state) {
    auto c3 = cc->EvalAtIndex(c1, 1);
  }
}
HE_MICRO_BENCHMARK(BM_Rotate1_Palisade_CKKS);

}  // namespace palisade
}  // namespace he
}  // namespace intel
