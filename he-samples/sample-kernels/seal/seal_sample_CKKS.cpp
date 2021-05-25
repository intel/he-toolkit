// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <seal/seal.h>

#include <chrono>
#include <random>
#include <vector>

#include "kernel_util.h"
#include "kernels/seal/seal_ckks_context.h"
#include "kernels/seal/seal_ckks_kernel_executor.h"
#include "kernels/seal/seal_omp_utils.h"

namespace intel {
namespace he {
namespace heseal {

template <class Dim1, class Dim2, class Dim3>
void BM_Seal_DotPlainBatchAxis_CKKS(benchmark::State& state, Dim1&& dim1,
                                    Dim2&& dim2, Dim3&& dim3) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, false, false);
  SealCKKSKernelExecutor kernel_executor(context);

  size_t batch_size = 1;

  std::vector<double> input1(dim1 * dim2, 7);
  std::vector<double> input2(dim2 * dim3, 8);

  std::vector<seal::Ciphertext> arg1 = context.encryptVector(
      gsl::span(input1.data(), input1.size()), batch_size);

  std::vector<seal::Plaintext> arg2 =
      context.encodeVector(gsl::span(input2.data(), input2.size()), batch_size);

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0, OMPUtilitiesS::assignOMPThreads(omp_remaining_threads, dim1 * dim3));

  for (auto _ : state) {
    kernel_executor.dotPlainBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}

BENCHMARK_CAPTURE(BM_Seal_DotPlainBatchAxis_CKKS, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Seal_DotPlainBatchAxis_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Seal_DotCipherBatchAxis_CKKS(benchmark::State& state, Dim1&& dim1,
                                     Dim2&& dim2, Dim3&& dim3) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, true, true);
  SealCKKSKernelExecutor kernel_executor(context);

  size_t batch_size = 1;

  std::vector<double> input1(dim1 * dim2, 7);
  std::vector<double> input2(dim2 * dim3, 8);

  std::vector<seal::Ciphertext> arg1 = context.encryptVector(
      gsl::span(input1.data(), input1.size()), batch_size);

  std::vector<seal::Ciphertext> arg2 = context.encryptVector(
      gsl::span(input2.data(), input2.size()), batch_size);

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0, OMPUtilitiesS::assignOMPThreads(omp_remaining_threads, dim1 * dim3));

  for (auto _ : state) {
    kernel_executor.dotCipherBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}

BENCHMARK_CAPTURE(BM_Seal_DotCipherBatchAxis_CKKS, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

BENCHMARK_CAPTURE(BM_Seal_DotCipherBatchAxis_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Seal_MatMulVal_CKKS(benchmark::State& state, Dim1&& dim1, Dim2&& dim2,
                            Dim3&& dim3) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, true, true);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<std::vector<double>> mat_A(dim1, std::vector<double>(dim2));
  std::vector<std::vector<double>> mat_B_T(dim3, std::vector<double>(dim2));
  std::default_random_engine rand_gen;
  std::uniform_real_distribution<double> uniform_rnd(-1.5, 1.5);
  for (std::size_t r = 0; r < mat_A.size(); ++r)
    for (std::size_t c = 0; c < mat_A[r].size(); ++c)
      mat_A[r][c] = uniform_rnd(rand_gen);
  for (std::size_t r = 0; r < mat_B_T.size(); ++r)
    for (std::size_t c = 0; c < mat_B_T[r].size(); ++c)
      mat_B_T[r][c] = uniform_rnd(rand_gen);

  std::vector<std::vector<seal::Ciphertext>> cipher_A(mat_A.size());
  std::vector<std::vector<seal::Ciphertext>> cipher_B_T(mat_B_T.size());
  for (std::size_t r = 0; r < mat_A.size(); ++r)
    cipher_A[r] = context.encryptVector(mat_A[r]);
  for (std::size_t r = 0; r < mat_B_T.size(); ++r)
    cipher_B_T[r] = context.encryptVector(mat_B_T[r]);

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0, OMPUtilitiesS::assignOMPThreads(omp_remaining_threads,
                                         mat_A.size() * mat_B_T.size()));

  for (auto _ : state) {
    kernel_executor.matMul(cipher_A, cipher_B_T, dim2);
  }

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}

BENCHMARK_CAPTURE(BM_Seal_MatMulVal_CKKS, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;
BENCHMARK_CAPTURE(BM_Seal_MatMulVal_CKKS, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

template <class Dim1, class Dim2>
void BM_Seal_LogisticRegression_CKKS(benchmark::State& state, Dim1&& n_inputs,
                                     Dim2&& n_weights) {
  SealCKKSContext context(state.range(0), std::vector<int>(state.range(1), 50),
                          1UL << 40, true, true);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> weights(n_weights);
  std::vector<std::vector<double>> inputs(n_inputs);

  std::default_random_engine rand_gen;
  std::uniform_real_distribution<double> uniform_rnd(-1.5, 1.5);
  for (std::size_t i = 0; i < weights.size(); ++i)
    weights[i] = uniform_rnd(rand_gen);
  for (std::size_t j = 0; j < inputs.size(); ++j) {
    inputs[j].resize(n_weights);
    for (std::size_t i = 0; i < inputs[j].size(); ++i)
      inputs[j][i] = uniform_rnd(rand_gen);
  }
  double bias = uniform_rnd(rand_gen);

  std::vector<seal::Ciphertext> cipher_weights =
      context.encryptVector(gsl::span(weights.data(), weights.size()),
                            context.encoder().slot_count());

  seal::Ciphertext cipher_bias;
  seal::Plaintext plain_bias;
  context.encoder().encode(bias, context.scale(), plain_bias);
  context.encryptor().encrypt(plain_bias, cipher_bias);

  std::vector<std::vector<seal::Ciphertext>> cipher_inputs(inputs.size());

  for (std::size_t inputs_r = 0; inputs_r < inputs.size(); ++inputs_r)
    cipher_inputs[inputs_r] = context.encryptVector(
        gsl::span(inputs[inputs_r].data(), inputs[inputs_r].size()),
        context.encoder().slot_count());
  std::vector<seal::Ciphertext> cipher_retval;

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0, OMPUtilitiesS::assignOMPThreads(omp_remaining_threads, inputs.size()));

  for (auto _s : state) {
    cipher_retval = kernel_executor.evaluateLogisticRegression(
        cipher_weights, cipher_inputs, cipher_bias, weights.size(), 3);
  }

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}

BENCHMARK_CAPTURE(BM_Seal_LogisticRegression_CKKS, (5x4), 5, 4)
    ->Unit(benchmark::kMillisecond)
    ->Args({16384, 6});

BENCHMARK_CAPTURE(BM_Seal_LogisticRegression_CKKS, (20x16), 20, 16)
    ->Unit(benchmark::kMillisecond)
    ->Args({16384, 6});

//=================================================================

}  // namespace heseal
}  // namespace he
}  // namespace intel
