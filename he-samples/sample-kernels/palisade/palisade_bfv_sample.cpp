// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <omp.h>
#include <palisade.h>

#include <algorithm>
#include <vector>

#include "kernel_util.h"
#include "kernels/palisade/palisade_bfv_kernel_executor.h"
#include "palisade_util.h"

namespace intel {
namespace he {
namespace palisade {

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_DotPlainBatchAxis_BFV(benchmark::State& state, Dim1&& dim1,
                                       Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<int64_t> input{0, 1, 2, 3};

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Plaintext> arg2(dim2 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(input);
    arg1[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    arg2[i] = cc->MakePackedPlaintext(input);
  }

  for (auto _ : state) {
    kernel_executor.dotPlainBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_DotPlainBatchAxis_BFV, (100x10)x(10x1), 100, 10,
                  1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_DotPlainBatchAxis_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_DotCipherBatchAxis_BFV(benchmark::State& state, Dim1&& dim1,
                                        Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1), 60));

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<int64_t> input{0, 1, 2, 3};

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg2(dim2 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(input);
    arg1[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(input);
    arg2[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (auto _ : state) {
    kernel_executor.dotCipherBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_DotCipherBatchAxis_BFV, (100x10)x(10x1), 100, 10,
                  1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_DotCipherBatchAxis_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;
//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_MatMulEIP_BFV(benchmark::State& state, Dim1&& dim1,
                               Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1)));

  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<int64_t> data(dim2, 7);

  // For Each Row in A
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(data);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(data);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (auto _ : state) {
    kernel_executor.matMulEIP(cipher_a, cipher_b, dim1, dim2, dim3, dim2);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_MatMulEIP_BFV, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_MatMulEIP_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_MatMulVal_BFV(benchmark::State& state, Dim1&& dim1,
                               Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1)));

  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<int64_t> data(dim2, 7);

  // For Each Row in A
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(data);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(data);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }
  for (auto _ : state) {
    kernel_executor.matMulVal(cipher_a, cipher_b, dim1, dim2, dim3);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_MatMulVal_BFV, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_MatMulVal_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_MatMulRow_BFV(benchmark::State& state, Dim1&& dim1,
                               Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeBFVContext(state.range(0),
                                       std::vector<int>(state.range(1)));
  int64_t slots = state.range(0);
  int64_t spacers = slots / dim2;

  int n = 0;
  std::vector<int32_t> vec(dim2);
  std::generate(std::begin(vec), std::end(vec),
                [&n, &spacers] { return n += spacers; });

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<int64_t> data(slots, 7);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> vec_cipher_a(dim1);
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(data);
    vec_cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }
  lbcrypto::Plaintext plain = cc->MakePackedPlaintext(data);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_b =
      cc->Encrypt(keys.publicKey, plain);
  plain.reset();

  const int old_max_active_levels = omp_get_max_active_levels();
  const int old_nested_value = omp_get_nested();
  omp_set_nested(true);
  omp_set_max_active_levels(2);
  for (auto _ : state) {
    kernel_executor.matMulRow(vec_cipher_a, cipher_b, dim1, dim2, dim3, slots);
  }
  omp_set_max_active_levels(old_max_active_levels);
  omp_set_nested(old_nested_value);
}

BENCHMARK_CAPTURE(BM_Palisade_MatMulRow_BFV, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_MatMulRow_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

}  // namespace palisade
}  // namespace he
}  // namespace intel
