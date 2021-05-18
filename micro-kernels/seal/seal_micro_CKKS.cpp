// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <seal/seal.h>

#include <vector>

#include "micro_util.h"
#include "seal/seal_ckks_context.h"

namespace intel {
namespace he {
namespace heseal {

static void BM_Encode_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  for (auto _ : state) {
    context.encoder().encode(input, context.scale(), plain);
  }
}
HE_MICRO_BENCHMARK(BM_Encode_Seal_CKKS);

//=================================================================

static void BM_Encrypt_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  context.encoder().encode(input, context.scale(), plain);

  for (auto _ : state) {
    seal::Ciphertext cipher;
    context.encryptor().encrypt(plain, cipher);
  }
}
HE_MICRO_BENCHMARK(BM_Encrypt_Seal_CKKS);

//=================================================================

static void BM_EncodeEncrypt_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  for (auto _ : state) {
    seal::Plaintext plain;
    seal::Ciphertext cipher;
    context.encoder().encode(input, context.scale(), plain);
    context.encryptor().encrypt(plain, cipher);
  }
}
HE_MICRO_BENCHMARK(BM_EncodeEncrypt_Seal_CKKS);

//=================================================================

static void BM_Decrypt_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher);

  for (auto _ : state) {
    seal::Plaintext plain2;
    context.decryptor().decrypt(cipher, plain);
  }
}
HE_MICRO_BENCHMARK(BM_Decrypt_Seal_CKKS);

//=================================================================

static void BM_Decode_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher);
  seal::Plaintext plain2;
  context.decryptor().decrypt(cipher, plain);

  for (auto _ : state) {
    context.encoder().decode(plain, input);
  }
}
HE_MICRO_BENCHMARK(BM_Decode_Seal_CKKS);

//=================================================================

static void BM_DecryptDecode_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher);

  for (auto _ : state) {
    seal::Plaintext plain2;
    context.decryptor().decrypt(cipher, plain);
    context.encoder().decode(plain, input);
  }
}
HE_MICRO_BENCHMARK(BM_DecryptDecode_Seal_CKKS);

//=================================================================

static void BM_Add_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().add(cipher1, cipher2, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_Add_Seal_CKKS);

//=================================================================

static void BM_Sub_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().sub(cipher1, cipher2, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_Sub_Seal_CKKS);

//=================================================================

static void BM_AddPlain_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().add_plain(cipher1, plain, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_AddPlain_Seal_CKKS);

//=================================================================

static void BM_SubPlain_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().sub_plain(cipher1, plain, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_SubPlain_Seal_CKKS);

//=================================================================

static void BM_Negate_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().negate(cipher1, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_Negate_Seal_CKKS);

//=================================================================

static void BM_Multiply_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 20, true, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().multiply(cipher1, cipher2, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_Multiply_Seal_CKKS);

//=================================================================

static void BM_MultiplyRelin_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 20, true, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().multiply(cipher1, cipher2, cipher3);
    context.evaluator().relinearize_inplace(cipher3, context.relin_keys());
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyRelin_Seal_CKKS);

//=================================================================
static void BM_MultiplyRelinRescale_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 20, true, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().multiply(cipher1, cipher2, cipher3);
    context.evaluator().relinearize_inplace(cipher3, context.relin_keys());
    context.evaluator().rescale_to_next_inplace(cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyRelinRescale_Seal_CKKS);

//=================================================================
static void BM_Rescale_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 20, true, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    state.PauseTiming();
    context.encryptor().encrypt(plain, cipher1);
    state.ResumeTiming();
    context.evaluator().rescale_to_next_inplace(cipher1);
  }
}
HE_MICRO_BENCHMARK(BM_Rescale_Seal_CKKS);

//=================================================================

static void BM_Square_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 20, true, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().square(cipher1, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_Square_Seal_CKKS);

//=================================================================

static void BM_MultiplyPlain_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 20, true, false);

  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().multiply_plain(cipher1, plain, cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyPlain_Seal_CKKS);

//=================================================================

static void BM_Rotate1_Seal_CKKS(benchmark::State& state) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 20, true, true);
  auto input = generateVector<double>(state.range(0) / 2);

  seal::Plaintext plain;
  seal::Ciphertext cipher1;
  seal::Ciphertext cipher2;
  context.encoder().encode(input, context.scale(), plain);
  context.encryptor().encrypt(plain, cipher1);
  context.encryptor().encrypt(plain, cipher2);

  for (auto _ : state) {
    seal::Ciphertext cipher3;
    context.evaluator().rotate_vector(cipher1, 1, context.galois_keys(),
                                      cipher3);
  }
}
HE_MICRO_BENCHMARK(BM_Rotate1_Seal_CKKS);

//=================================================================

}  // namespace heseal
}  // namespace he
}  // namespace intel
