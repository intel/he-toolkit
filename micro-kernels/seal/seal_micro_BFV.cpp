// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <seal/seal.h>

#include <cstddef>
#include <memory>
#include <numeric>
#include <vector>

#include "micro_util.h"
#include "seal/seal_bfv_context.h"

namespace intel {
namespace he {
namespace heseal {

static void BM_Encode_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  for (auto _ : state) {
    seal::Plaintext plain_matrix;
    context.batch_encoder().encode(pod_matrix, plain_matrix);
  }
}
HE_MICRO_BENCHMARK(BM_Encode_Seal_BFV);

//=================================================================

static void BM_Encrypt_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix;
    context.encryptor().encrypt(plain_matrix, encrypted_matrix);
  }
}
HE_MICRO_BENCHMARK(BM_Encrypt_Seal_BFV);

//=================================================================

static void BM_EncodeEncrypt_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  for (auto _ : state) {
    seal::Plaintext plain_matrix;
    context.batch_encoder().encode(pod_matrix, plain_matrix);
    seal::Ciphertext encrypted_matrix;
    context.encryptor().encrypt(plain_matrix, encrypted_matrix);
  }
}
HE_MICRO_BENCHMARK(BM_EncodeEncrypt_Seal_BFV);

//=================================================================

static void BM_Decrypt_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  seal::Ciphertext encrypted_matrix;
  context.encryptor().encrypt(plain_matrix, encrypted_matrix);

  for (auto _ : state) {
    seal::Plaintext plain_result;
    context.decryptor().decrypt(encrypted_matrix, plain_result);
  }
}
HE_MICRO_BENCHMARK(BM_Decrypt_Seal_BFV);

//=================================================================

static void BM_Decode_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  std::vector<std::uint64_t> pod_result;
  for (auto _ : state) {
    context.batch_encoder().decode(plain_matrix, pod_result);
  }
}
HE_MICRO_BENCHMARK(BM_Decode_Seal_BFV);

//=================================================================

static void BM_DecryptDecode_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  seal::Ciphertext encrypted_matrix;
  context.encryptor().encrypt(plain_matrix, encrypted_matrix);

  for (auto _ : state) {
    seal::Plaintext plain_result;
    context.decryptor().decrypt(encrypted_matrix, plain_result);
    std::vector<std::uint64_t> pod_result;
    context.batch_encoder().decode(plain_result, pod_result);
  }
}
HE_MICRO_BENCHMARK(BM_DecryptDecode_Seal_BFV);

//=================================================================

static void BM_Add_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  seal::Ciphertext encrypted_matrix;
  context.encryptor().encrypt(plain_matrix, encrypted_matrix);

  std::vector<std::uint64_t> pod_matrix2;
  for (size_t i = 0; i < slot_count; i++) {
    pod_matrix2.push_back((i % 2) + 1);
  }
  seal::Plaintext plain_matrix2;
  context.batch_encoder().encode(pod_matrix2, plain_matrix2);
  seal::Ciphertext encrypted_matrix2;
  context.encryptor().encrypt(plain_matrix2, encrypted_matrix2);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().add(encrypted_matrix, encrypted_matrix2,
                            encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_Add_Seal_BFV);

//=================================================================

static void BM_Sub_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  seal::Ciphertext encrypted_matrix;
  context.encryptor().encrypt(plain_matrix, encrypted_matrix);

  std::vector<std::uint64_t> pod_matrix2;
  for (size_t i = 0; i < slot_count; i++) {
    pod_matrix2.push_back((i % 2) + 1);
  }
  seal::Plaintext plain_matrix2;
  context.batch_encoder().encode(pod_matrix2, plain_matrix2);
  seal::Ciphertext encrypted_matrix2;
  context.encryptor().encrypt(plain_matrix2, encrypted_matrix2);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().sub(encrypted_matrix, encrypted_matrix2,
                            encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_Sub_Seal_BFV);

//=================================================================

static void BM_AddPlain_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  seal::Ciphertext encrypted_matrix;
  context.encryptor().encrypt(plain_matrix, encrypted_matrix);

  std::vector<std::uint64_t> pod_matrix2;
  for (size_t i = 0; i < slot_count; i++) {
    pod_matrix2.push_back((i % 2) + 1);
  }
  seal::Plaintext plain_matrix2;
  context.batch_encoder().encode(pod_matrix2, plain_matrix2);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().add_plain(encrypted_matrix, plain_matrix2,
                                  encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_AddPlain_Seal_BFV);

//=================================================================

static void BM_SubPlain_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  seal::Ciphertext encrypted_matrix;
  context.encryptor().encrypt(plain_matrix, encrypted_matrix);

  std::vector<std::uint64_t> pod_matrix2;
  for (size_t i = 0; i < slot_count; i++) {
    pod_matrix2.push_back((i % 2) + 1);
  }
  seal::Plaintext plain_matrix2;
  context.batch_encoder().encode(pod_matrix2, plain_matrix2);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().sub_plain(encrypted_matrix, plain_matrix2,
                                  encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_SubPlain_Seal_BFV);

//=================================================================

static void BM_Negate_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix;
  context.batch_encoder().encode(pod_matrix, plain_matrix);

  seal::Ciphertext encrypted_matrix;
  context.encryptor().encrypt(plain_matrix, encrypted_matrix);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().negate(encrypted_matrix, encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_Negate_Seal_BFV);

//=================================================================

static void BM_Multiply_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix1;
  context.batch_encoder().encode(pod_matrix, plain_matrix1);

  std::vector<std::uint64_t> pod_result;

  seal::Ciphertext encrypted_matrix1;
  context.encryptor().encrypt(plain_matrix1, encrypted_matrix1);

  std::vector<std::uint64_t> pod_matrix2;
  for (size_t i = 0; i < slot_count; i++) {
    pod_matrix2.push_back((i % 2) + 1);
  }
  seal::Plaintext plain_matrix2;
  context.batch_encoder().encode(pod_matrix2, plain_matrix2);
  seal::Ciphertext encrypted_matrix2;
  context.encryptor().encrypt(plain_matrix2, encrypted_matrix2);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().multiply(encrypted_matrix1, encrypted_matrix2,
                                 encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_Multiply_Seal_BFV);

//=================================================================

static void BM_MultiplyRelin_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         true, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix1;
  context.batch_encoder().encode(pod_matrix, plain_matrix1);

  std::vector<std::uint64_t> pod_result;

  seal::Ciphertext encrypted_matrix1;
  context.encryptor().encrypt(plain_matrix1, encrypted_matrix1);

  std::vector<std::uint64_t> pod_matrix2;
  for (size_t i = 0; i < slot_count; i++) {
    pod_matrix2.push_back((i % 2) + 1);
  }
  seal::Plaintext plain_matrix2;
  context.batch_encoder().encode(pod_matrix2, plain_matrix2);
  seal::Ciphertext encrypted_matrix2;
  context.encryptor().encrypt(plain_matrix2, encrypted_matrix2);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().multiply(encrypted_matrix1, encrypted_matrix2,
                                 encrypted_matrix3);
    context.evaluator().relinearize_inplace(encrypted_matrix3,
                                            context.relin_keys());
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyRelin_Seal_BFV);

//=================================================================

static void BM_Square_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         false, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix1;
  context.batch_encoder().encode(pod_matrix, plain_matrix1);

  seal::Ciphertext encrypted_matrix1;
  context.encryptor().encrypt(plain_matrix1, encrypted_matrix1);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().square(encrypted_matrix1, encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_Square_Seal_BFV);

//=================================================================

static void BM_MultiplyPlain_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         true, false);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix1;
  context.batch_encoder().encode(pod_matrix, plain_matrix1);

  seal::Ciphertext encrypted_matrix1;
  context.encryptor().encrypt(plain_matrix1, encrypted_matrix1);

  for (auto _ : state) {
    seal::Ciphertext encrypted_matrix3;
    context.evaluator().multiply_plain(encrypted_matrix1, plain_matrix1,
                                       encrypted_matrix3);
  }
}
HE_MICRO_BENCHMARK(BM_MultiplyPlain_Seal_BFV);

//=================================================================

static void BM_Rotate1_Seal_BFV(benchmark::State& state) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         true, true);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto pod_matrix = generateVector<std::uint64_t>(slot_count, row_size);

  seal::Plaintext plain_matrix1;
  context.batch_encoder().encode(pod_matrix, plain_matrix1);

  seal::Ciphertext encrypted_matrix1;
  context.encryptor().encrypt(plain_matrix1, encrypted_matrix1);

  if (context.context().using_keyswitching()) {
    for (auto _ : state) {
      context.evaluator().rotate_rows_inplace(encrypted_matrix1, 1,
                                              context.galois_keys());
    }
  }
}
HE_MICRO_BENCHMARK(BM_Rotate1_Seal_BFV);

//=================================================================

}  // namespace heseal
}  // namespace he
}  // namespace intel
