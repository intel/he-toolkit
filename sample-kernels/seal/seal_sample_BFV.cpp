// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <benchmark/benchmark.h>
#include <omp.h>
#include <seal/seal.h>

#include <vector>

#include "kernel_util.h"
#include "kernels/seal/seal_bfv_context.h"
#include "kernels/seal/seal_bfv_kernel_executor.h"
#include "kernels/seal/seal_omp_utils.h"

namespace intel {
namespace he {
namespace heseal {

template <class Dim1, class Dim2, class Dim3>
void BM_Seal_DotPlainBatchAxis_BFV(benchmark::State& state, Dim1&& dim1,
                                   Dim2&& dim2, Dim3&& dim3) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         true, true);
  SealBFVKernelExecutor kernel_executor(context);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto input = generateVector<std::uint64_t>(slot_count, row_size);

  std::vector<seal::Ciphertext> arg1(dim1 * dim2);
  std::vector<seal::Plaintext> arg2(dim2 * dim3);
  std::vector<seal::Ciphertext> out(dim1 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    seal::Plaintext plain;
    seal::Ciphertext cipher;
    context.batch_encoder().encode(input, plain);
    context.encryptor().encrypt(plain, cipher);
    arg1[i] = cipher;
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    seal::Plaintext plain;
    context.batch_encoder().encode(input, plain);
    arg2[i] = plain;
  }

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0, OMPUtilitiesS::assignOMPThreads(omp_remaining_threads, dim1 * dim3));

  for (auto _ : state) {
    kernel_executor.dotPlainBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}

// The following two tests need only 2GB memory to run the tests.
BENCHMARK_CAPTURE(BM_Seal_DotPlainBatchAxis_BFV, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;
BENCHMARK_CAPTURE(BM_Seal_DotPlainBatchAxis_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Seal_DotCipherBatchAxis_BFV(benchmark::State& state, Dim1&& dim1,
                                    Dim2&& dim2, Dim3&& dim3) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         true, true);
  SealBFVKernelExecutor kernel_executor(context);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;
  auto input = generateVector<std::uint64_t>(slot_count, row_size);

  std::vector<seal::Ciphertext> arg1(dim1 * dim2);
  std::vector<seal::Ciphertext> arg2(dim2 * dim3);
  std::vector<seal::Ciphertext> out(dim1 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    seal::Plaintext plain;
    seal::Ciphertext cipher;
    context.batch_encoder().encode(input, plain);
    context.encryptor().encrypt(plain, cipher);
    arg1[i] = cipher;
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    seal::Plaintext plain;
    seal::Ciphertext cipher;
    context.batch_encoder().encode(input, plain);
    context.encryptor().encrypt(plain, cipher);
    arg2[i] = cipher;
  }

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0, OMPUtilitiesS::assignOMPThreads(omp_remaining_threads, dim1 * dim3));

  for (auto _ : state) {
    kernel_executor.dotCipherBatchAxis(arg1, arg2, dim1, dim2, dim3);
  }

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}

// The following two tests need only 2GB memory to run the tests.
BENCHMARK_CAPTURE(BM_Seal_DotCipherBatchAxis_BFV, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;
BENCHMARK_CAPTURE(BM_Seal_DotCipherBatchAxis_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Seal_MatMulVal_BFV(benchmark::State& state, Dim1&& dim1, Dim2&& dim2,
                           Dim3&& dim3) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         true, true);
  SealBFVKernelExecutor kernel_executor(context);

  std::vector<std::vector<int>> my_mat_a(dim1, std::vector<int>(dim2));
  std::vector<std::vector<int>> my_mat_b(dim2, std::vector<int>(dim3));

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;

  auto vec_a = generateVector<std::uint64_t>(slot_count, row_size);
  auto vec_b = generateVector<std::uint64_t>(slot_count, row_size);

  // Keeping the below steps (even though real data isn't being operated on)
  // will allow for easy understanding of the algorithm
  // Get simple transpose of Matrix B
  std::vector<std::vector<int>> my_trans_b(my_mat_b[0].size(),
                                           std::vector<int>(my_mat_b.size()));
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_trans_b[j][i] = my_mat_b[i][j];

  // 2d vector for each row/col in Matrix A and trans_matrix B
  std::vector<std::vector<uint64_t>> vec_container_a(dim1, vec_a);
  std::vector<std::vector<uint64_t>> vec_container_b(dim3, vec_b);

  // Vectors of plaintexts and ciphertexts
  // 1 for each row of Matrix A and of Trans_Matrix B
  std::vector<seal::Plaintext> vec_pt_a(dim1), vec_pt_b(dim3);
  std::vector<seal::Ciphertext> vec_ct_a(dim1), vec_ct_b(dim3);

  // Ciphertext result for output on server
  std::vector<std::vector<seal::Ciphertext>> vec_ct_res(
      vec_ct_a.size(), std::vector<seal::Ciphertext>(vec_ct_b));

  for (size_t i = 0; i < dim1; i++)
    context.batch_encoder().encode(vec_container_a[i], vec_pt_a[i]);
  for (size_t i = 0; i < dim3; i++)
    context.batch_encoder().encode(vec_container_b[i], vec_pt_b[i]);

  for (size_t i = 0; i < dim1; i++)
    context.encryptor().encrypt(vec_pt_a[i], vec_ct_a[i]);
  for (size_t i = 0; i < dim3; i++)
    context.encryptor().encrypt(vec_pt_b[i], vec_ct_b[i]);

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0, OMPUtilitiesS::assignOMPThreads(omp_remaining_threads, dim1 * dim3));

  for (auto _ : state) {
    kernel_executor.matMulVal(vec_ct_a, vec_ct_b, dim1, dim2, dim3);
  }

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}
BENCHMARK_CAPTURE(BM_Seal_MatMulVal_BFV, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;
BENCHMARK_CAPTURE(BM_Seal_MatMulVal_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

template <class Dim1, class Dim2, class Dim3>
void BM_Seal_MatMulRow_BFV(benchmark::State& state, Dim1&& dim1, Dim2&& dim2,
                           Dim3&& dim3) {
  SealBFVContext context(state.range(0), std::vector<int>(state.range(1), 50),
                         true, true);
  SealBFVKernelExecutor kernel_executor(context);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;

  auto vec_a = generateVector<std::uint64_t>(slot_count, row_size);
  auto vec_b = generateVector<std::uint64_t>(slot_count, row_size);

  std::vector<std::vector<uint64_t>> vec_container_a((dim1 + 1) / 2, vec_a);

  // Plaintexts and Ciphertexts for input
  seal::Plaintext pt_b;
  std::vector<seal::Plaintext> vec_pt_a(vec_container_a.size());
  seal::Ciphertext ct_b;
  std::vector<seal::Ciphertext> vec_ct_a(vec_container_a.size());

  // Encoding vectors of input into plaintext vectors
  // (For Matrix A, one for every two rows)
  for (size_t i = 0; i < vec_container_a.size(); i++)
    context.batch_encoder().encode(vec_container_a[i], vec_pt_a[i]);
  context.batch_encoder().encode(vec_b, pt_b);

  // Encrypting vectors of plaintext into ciphertext vectors
  // (For Matrix A, one for every two rows)
  for (size_t i = 0; i < vec_pt_a.size(); i++)
    context.encryptor().encrypt(vec_pt_a[i], vec_ct_a[i]);
  context.encryptor().encrypt(pt_b, ct_b);
  vec_pt_a.clear();

  int omp_remaining_threads = OMPUtilitiesS::MaxThreads;
  OMPUtilitiesS::setThreadsAtLevel(
      0,
      OMPUtilitiesS::assignOMPThreads(omp_remaining_threads, vec_ct_a.size()));
  int inner_threads = omp_remaining_threads / vec_ct_a.size();
  if (inner_threads > dim2 - 1)
    inner_threads = dim2 - 1;
  else if (inner_threads <= 0)
    inner_threads = 1;
  if (inner_threads > 1)
    OMPUtilitiesS::assignOMPThreads(omp_remaining_threads,
                                    inner_threads * vec_ct_a.size());
  OMPUtilitiesS::setThreadsAtLevel(1, inner_threads);

  const int old_max_active_levels = omp_get_max_active_levels();
  const int old_nested_value = omp_get_nested();
  omp_set_nested(true);
  omp_set_max_active_levels(2);
  for (auto _ : state) {
    auto sum = kernel_executor.matMulRow(vec_ct_a, ct_b, dim1, dim2, dim3);
  }
  omp_set_max_active_levels(old_max_active_levels);
  omp_set_nested(old_nested_value);

  OMPUtilitiesS::setThreadsAtLevel(0, OMPUtilitiesS::MaxThreads);
}

BENCHMARK_CAPTURE(BM_Seal_MatMulRow_BFV, (100x10)x(10x1), 100, 10, 1)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;
BENCHMARK_CAPTURE(BM_Seal_MatMulRow_BFV, (10x9)x(9x8), 10, 9, 8)
    ->Unit(benchmark::kMillisecond)
    ->ADD_SAMPLE_HE_ARGS;

//=================================================================

}  // namespace heseal
}  // namespace he
}  // namespace intel
