// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <omp.h>
#include <palisade.h>

#include <algorithm>
#include <vector>

#include "kernel_util.h"
#include "kernels/palisade/palisade_ckks_kernel_executor.h"
#include "palisade_util.h"

namespace intel {
namespace he {
namespace palisade {

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_DotPlainBatchAxis_CKKS(benchmark::State& state, Dim1&& dim1,
                                        Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(
      cc, keys.publicKey, lbcrypto::RescalingTechnique::APPROXAUTO);

  std::vector<double> input{0.0, 1.1, 2.2, 3.3};

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Plaintext> arg2(dim2 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(input);
    auto cipher = cc->Encrypt(keys.publicKey, plain);
    arg1[i] = cipher;
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(input);
    arg2[i] = plain;
  }

  for (auto _ : state) {
    kernel_executor.dotPlainBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_DotPlainBatchAxis_CKKS, (100x10)x(10x1), 100, 10,
                  1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_DotPlainBatchAxis_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_DotCipherBatchAxis_CKKS(benchmark::State& state, Dim1&& dim1,
                                         Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(
      cc, keys.publicKey, lbcrypto::RescalingTechnique::APPROXAUTO);

  std::vector<double> input{0.0, 1.1, 2.2, 3.3};

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg2(dim2 * dim3);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> out(dim1 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(input);
    auto cipher = cc->Encrypt(keys.publicKey, plain);
    arg1[i] = cipher;
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(input);
    auto cipher = cc->Encrypt(keys.publicKey, plain);
    arg2[i] = cipher;
  }

  for (auto _ : state) {
    kernel_executor.dotCipherBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_DotCipherBatchAxis_CKKS, (100x10)x(10x1), 100, 10,
                  1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_DotCipherBatchAxis_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_MatMulEIP_CKKS(benchmark::State& state, Dim1&& dim1,
                                Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1)));

  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<double> data(dim2, 7.0);

  // For Each Row in A
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(data);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(data);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (auto _ : state) {
    kernel_executor.matMulEIP(cipher_a, cipher_b, dim1, dim2, dim3, dim2);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_MatMulEIP_CKKS, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_MatMulEIP_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_MatMulVal_CKKS(benchmark::State& state, Dim1&& dim1,
                                Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1), 60));

  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(
      cc, keys.publicKey, lbcrypto::RescalingTechnique::APPROXRESCALE);

  std::vector<double> data(dim2, 7.0);

  // For Each Row in A
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(data);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(data);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }
  for (auto _ : state) {
    kernel_executor.matMulVal(cipher_a, cipher_b, dim1, dim2, dim3);
  }
}

BENCHMARK_CAPTURE(BM_Palisade_MatMulVal_CKKS, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_MatMulVal_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

template <class Dim1, class Dim2, class Dim3>
void BM_Palisade_MatMulRow_CKKS(benchmark::State& state, Dim1&& dim1,
                                Dim2&& dim2, Dim3&& dim3) {
  auto cc = generatePalisadeCKKSContext(state.range(0),
                                        std::vector<int>(state.range(1)));

  int64_t slots = state.range(0) / 2;
  int64_t spacers = slots / dim2;

  int n = 0;
  std::vector<int32_t> vec(dim2);
  std::generate(std::begin(vec), std::end(vec),
                [&n, &spacers] { return n += spacers; });

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<double> data(slots, 7.0);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> vec_cipher_a(dim1);
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(data);
    vec_cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }
  lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(data);
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

BENCHMARK_CAPTURE(BM_Palisade_MatMulRow_CKKS, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_MatMulRow_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

template <class Dim1, class Dim2>
void BM_Palisade_LogisticRegression_CKKS(benchmark::State& state,
                                         Dim1&& n_inputs, Dim2&& n_weights) {
  std::vector<double> weights(n_weights);
  std::vector<std::vector<double>> inputs(n_inputs);

  std::default_random_engine rand_gen;
  std::uniform_real_distribution<double> uniform_rnd(-1.5, 1.5);
  for (size_t i = 0; i < weights.size(); ++i)
    weights[i] = uniform_rnd(rand_gen);
  for (size_t j = 0; j < inputs.size(); ++j) {
    inputs[j].resize(n_weights);
    for (size_t i = 0; i < inputs[j].size(); ++i)
      inputs[j][i] = uniform_rnd(rand_gen);
  }

  double b = uniform_rnd(rand_gen);
  uint32_t batch_size = weights.size();
  uint32_t mult_depth = 5;
  uint32_t scale_factor_bits = 45;
  lbcrypto::SecurityLevel security_level =
      lbcrypto::SecurityLevel::HEStd_128_classic;
  lbcrypto::RescalingTechnique rs_tech =
      lbcrypto::RescalingTechnique::APPROXAUTO;
  lbcrypto::CryptoContext<lbcrypto::DCRTPoly> cc =
      lbcrypto::CryptoContextFactory<lbcrypto::DCRTPoly>::genCryptoContextCKKS(
          mult_depth, scale_factor_bits, batch_size, security_level, 0,
          rs_tech);
  cc->Enable(ENCRYPTION);
  cc->Enable(SHE);
  cc->Enable(LEVELEDSHE);

  lbcrypto::LPKeyPair<lbcrypto::DCRTPoly> key_pair = cc->KeyGen();
  cc->EvalMultKeyGen(key_pair.secretKey);
  cc->EvalSumKeyGen(key_pair.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(cc, key_pair.publicKey, rs_tech);

  std::vector<int32_t> il(inputs.size());
  for (int32_t i = 0; i < il.size(); ++i) il[i] = -i - 1;

  cc->EvalAtIndexKeyGen(key_pair.secretKey, il);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_inputs;
  cipher_inputs.reserve(inputs.size());
  lbcrypto::Plaintext tmp_plain;
  for (size_t i = 0; i < inputs.size(); ++i) {
    const auto& tmp = inputs[i];
    tmp_plain = cc->MakeCKKSPackedPlaintext(tmp);
    cipher_inputs.push_back(cc->Encrypt(key_pair.publicKey, tmp_plain));
  }

  tmp_plain = cc->MakeCKKSPackedPlaintext(weights);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_weights =
      cc->Encrypt(key_pair.publicKey, tmp_plain);
  std::vector<double> tmp_bias(inputs.size());
  std::fill(tmp_bias.begin(), tmp_bias.end(), b);
  tmp_plain = cc->MakeCKKSPackedPlaintext(tmp_bias);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_bias =
      cc->Encrypt(key_pair.publicKey, tmp_plain);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_weights_out;
  for (auto _s : state) {
    cipher_weights_out = kernel_executor.evaluateLogisticRegression(
        cipher_weights, cipher_inputs, cipher_bias, weights.size());
  }
}

BENCHMARK_CAPTURE(BM_Palisade_LogisticRegression_CKKS, (5x4), 5, 4)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Palisade_LogisticRegression_CKKS, (20x16), 20, 16)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

}  // namespace palisade
}  // namespace he
}  // namespace intel
