// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <memory>
#include <vector>

#include "kernels/palisade/palisade_bfv_kernel_executor.h"
#include "kernels/palisade/palisade_util.h"
#include "test_util.h"

namespace intel {
namespace he {
namespace palisade {

std::vector<int64_t> testDotCipherBatchAxis(const std::vector<int64_t>& input1,
                                            const std::vector<int64_t>& input2,
                                            size_t dim1, size_t dim2,
                                            size_t dim3) {
  auto cc = generatePalisadeBFVContext(8192, std::vector<int>(3, 60));

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg2(dim2 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain =
        cc->MakePackedPlaintext(std::vector<int64_t>{input1[i]});
    arg1[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    lbcrypto::Plaintext plain =
        cc->MakePackedPlaintext(std::vector<int64_t>{input2[i]});
    arg2[i] = cc->Encrypt(keys.publicKey, plain);
  }

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_out =
      kernel_executor.dotCipherBatchAxis(arg1, arg2, dim1, dim2, dim3);

  std::vector<int64_t> plain_out;
  for (const auto& cipher : cipher_out) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, cipher, &result);
    plain_out.push_back(result->GetPackedValue()[0]);
  }
  return plain_out;
}

std::vector<int64_t> testDotPlainBatchAxis(const std::vector<int64_t>& input1,
                                           const std::vector<int64_t>& input2,
                                           size_t dim1, size_t dim2,
                                           size_t dim3) {
  auto cc = generatePalisadeBFVContext(8192, std::vector<int>(3, 60));

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Plaintext> arg2(dim2 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain =
        cc->MakePackedPlaintext(std::vector<int64_t>{input1[i]});
    arg1[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    arg2[i] = cc->MakePackedPlaintext(std::vector<int64_t>{input2[i]});
  }

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_out =
      kernel_executor.dotPlainBatchAxis(arg1, arg2, dim1, dim2, dim3);

  std::vector<int64_t> plain_out;
  for (const auto& cipher : cipher_out) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, cipher, &result);
    plain_out.push_back(result->GetPackedValue()[0]);
  }
  return plain_out;
}

std::vector<std::vector<int64_t>> testMatMulEIP(
    const std::vector<std::vector<int64_t>>& my_mat_a,
    const std::vector<std::vector<int64_t>>& my_trans_b, size_t dim1,
    size_t dim2, size_t dim3) {
  int poly_mod_degree = 4096;
  auto cc = generatePalisadeBFVContext(poly_mod_degree, std::vector<int>(3));

  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);

  // For Each Row in A
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(my_mat_a[i]);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(my_trans_b[i]);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // One Ciphertext for each value in the resulting matrix
  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> sum(
      dim1, std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>(dim3));

  sum = kernel_executor.matMulEIP(cipher_a, cipher_b, dim1, dim2, dim3, dim2);

  std::vector<std::vector<lbcrypto::Plaintext>> sum_plain(
      dim1, std::vector<lbcrypto::Plaintext>(dim3));
  std::vector<std::vector<int64_t>> ret_mat_he(dim1,
                                               std::vector<int64_t>(dim3));

  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      cc->Decrypt(keys.secretKey, sum[i][j], &sum_plain[i][j]);
      ret_mat_he[i][j] = sum_plain[i][j]->GetPackedValue()[0];
    }
  }
  return ret_mat_he;
}

std::vector<std::vector<int64_t>> testMatMulRow(
    const std::vector<std::vector<int64_t>>& my_mat_a,
    const std::vector<std::vector<int64_t>>& my_mat_b, size_t dim1, size_t dim2,
    size_t dim3) {
  int poly_modulus_degree = 4096;
  auto cc =
      generatePalisadeBFVContext(poly_modulus_degree, std::vector<int>(3));
  size_t batch_size = poly_modulus_degree;

  int64_t spacers = poly_modulus_degree / dim2;

  std::vector<int32_t> vec(dim2);
  int n = 0;
  std::generate(std::begin(vec), std::end(vec),
                [&n, &spacers] { return n += spacers; });

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> vec_cipher_a(dim1);

  std::vector<int64_t> vec_a(poly_modulus_degree, 0);
  std::vector<int64_t> vec_b(poly_modulus_degree, 0);
  std::vector<std::vector<int64_t>> vec_container_a(dim1);

  for (size_t i = 0; i < dim1; i++) {
#pragma omp parallel for collapse(2)
    for (size_t j = 0; j < dim2; j++) {
      for (size_t k = 0; k < dim3; k++) {
        vec_a[spacers * j + k] = static_cast<int64_t>(my_mat_a[i][j]);
        if (i == 0) {
          vec_b[spacers * j + k] = static_cast<int64_t>(my_mat_b[j][k]);
        }
      }
    }
    vec_container_a[i] = vec_a;
  }

  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(vec_container_a[i]);
    auto cipher = cc->Encrypt(keys.publicKey, plain);
    vec_cipher_a[i] = cipher;
  }
  lbcrypto::Plaintext plain = cc->MakePackedPlaintext(vec_b);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_b =
      cc->Encrypt(keys.publicKey, plain);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> sum =
      kernel_executor.matMulRow(vec_cipher_a, cipher_b, dim1, dim2, dim3,
                                poly_modulus_degree);

  std::vector<std::vector<int64_t>> vec_ct_res(sum.size());
#pragma omp parallel for
  for (size_t i = 0; i < sum.size(); i++) {
    lbcrypto::Plaintext sum_plain;
    cc->Decrypt(keys.secretKey, sum[i], &sum_plain);
    vec_ct_res[i] = sum_plain->GetPackedValue();
    vec_ct_res[i].resize(dim3);
  }
  return vec_ct_res;
}

std::vector<std::vector<int64_t>> testMatMulVal(
    const std::vector<std::vector<int64_t>>& my_mat_a,
    const std::vector<std::vector<int64_t>>& my_trans_b, size_t dim1,
    size_t dim2, size_t dim3) {
  int poly_modulus_degree = 4096;
  auto cc =
      generatePalisadeBFVContext(poly_modulus_degree, std::vector<int>(3));

  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeBFVKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);

  // For Each Row in A
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(my_mat_a[i]);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakePackedPlaintext(my_trans_b[i]);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // One Ciphertext for each value in the resulting matrix
  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> sum =
      kernel_executor.matMulVal(cipher_a, cipher_b, dim1, dim2, dim3);

  std::vector<std::vector<int64_t>> ret_mat_he(dim1,
                                               std::vector<int64_t>(dim3));
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      lbcrypto::Plaintext sum_plain;
      cc->Decrypt(keys.secretKey, sum[i][j], &sum_plain);
      ret_mat_he[i][j] = sum_plain->GetPackedValue()[0];
    }
  }
  return ret_mat_he;
}

TEST(palisade_bfv_kernel_executor, dotPlainBatchAxis2x2x2) {
  std::vector<int64_t> input1{1, 2, 3, 4};
  std::vector<int64_t> input2{1, 2, 3, 4};
  std::vector<int64_t> exp_out{7, 10, 15, 22};

  std::vector<int64_t> out = testDotPlainBatchAxis(input1, input2, 2, 2, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_bfv_kernel_executor, dotPlainBatchAxis4x3x2) {
  std::vector<int64_t> input1{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<int64_t> input2{1, 2, 3, 4, 5, 6};
  std::vector<int64_t> exp_out{38, 44, 50, 56, 83, 98, 113, 128};

  std::vector<int64_t> out = testDotPlainBatchAxis(input1, input2, 4, 3, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_bfv_kernel_executor, dotCipherBatchAxis2x2x2) {
  std::vector<int64_t> input1{1, 2, 3, 4};
  std::vector<int64_t> input2{1, 2, 3, 4};
  std::vector<int64_t> exp_out{7, 10, 15, 22};

  std::vector<int64_t> out = testDotPlainBatchAxis(input1, input2, 2, 2, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_bfv_kernel_executor, dotCipherBatchAxis4x3x2) {
  std::vector<int64_t> input1{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<int64_t> input2{1, 2, 3, 4, 5, 6};
  std::vector<int64_t> exp_out{38, 44, 50, 56, 83, 98, 113, 128};

  std::vector<int64_t> out = testDotCipherBatchAxis(input1, input2, 4, 3, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_bfv_kernel_executor, MatMulEIP10x9x8) {
  size_t dim1 = 10;
  size_t dim2 = 9;
  size_t dim3 = 8;

  std::vector<std::vector<int64_t>> my_mat_a(dim1, std::vector<int64_t>(dim2));
  std::vector<std::vector<int64_t>> my_mat_b(dim2, std::vector<int64_t>(dim3));
  std::vector<std::vector<int64_t>> my_trans_b(dim3,
                                               std::vector<int64_t>(dim2));

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, 10);
  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++) my_mat_a[i][j] = distrib(gen);
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_mat_b[i][j] = distrib(gen);

#pragma omp parallel for collapse(2)
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_trans_b[j][i] = my_mat_b[i][j];

  std::vector<std::vector<int64_t>> out =
      testMatMulEIP(my_mat_a, my_trans_b, dim1, dim2, dim3);

  std::vector<std::vector<int64_t>> expected_out(dim1,
                                                 std::vector<int64_t>(dim3));

  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        expected_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }
  checkEqual(out, expected_out);
}

TEST(palisade_bfv_kernel_executor, MatMulEIP4x3x2) {
  size_t dim1 = 4;
  size_t dim2 = 3;
  size_t dim3 = 2;

  // Row-major
  std::vector<std::vector<int64_t>> my_mat_a{
      {1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}};
  std::vector<std::vector<int64_t>> my_trans_b{{1, 3, 5}, {2, 4, 6}};

  //  Row-major
  std::vector<std::vector<int64_t>> expected_out{
      {22, 28}, {49, 64}, {76, 100}, {103, 136}};

  std::vector<std::vector<int64_t>> out =
      testMatMulEIP(my_mat_a, my_trans_b, dim1, dim2, dim3);

  checkEqual(out, expected_out);
}

TEST(palisade_bfv_kernel_executor, MatMulVal10x9x8) {
  size_t dim1 = 10;
  size_t dim2 = 9;
  size_t dim3 = 8;

  std::vector<std::vector<int64_t>> my_mat_a(dim1, std::vector<int64_t>(dim2));
  std::vector<std::vector<int64_t>> my_mat_b(dim2, std::vector<int64_t>(dim3));
  std::vector<std::vector<int64_t>> my_trans_b(dim3,
                                               std::vector<int64_t>(dim2));

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, 10);
  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++) my_mat_a[i][j] = distrib(gen);
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_mat_b[i][j] = distrib(gen);

  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_trans_b[j][i] = my_mat_b[i][j];

  std::vector<std::vector<int64_t>> out =
      testMatMulVal(my_mat_a, my_trans_b, dim1, dim2, dim3);

  std::vector<std::vector<int64_t>> expected_out(dim1,
                                                 std::vector<int64_t>(dim3));
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        expected_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }
  checkEqual(expected_out, out);
}

TEST(palisade_bfv_kernel_executor, MatMulVal4x3x2) {
  size_t dim1 = 4;
  size_t dim2 = 3;
  size_t dim3 = 2;

  // Row-major
  std::vector<std::vector<int64_t>> my_mat_a{
      {1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}};
  std::vector<std::vector<int64_t>> my_trans_b{{1, 3, 5}, {2, 4, 6}};

  //  Row-major
  std::vector<std::vector<int64_t>> expected_out{
      {22, 28}, {49, 64}, {76, 100}, {103, 136}};

  std::vector<std::vector<int64_t>> out =
      testMatMulVal(my_mat_a, my_trans_b, dim1, dim2, dim3);

  checkEqual(out, expected_out);
}

TEST(palisade_bfv_kernel_executor, MatMulRow10x9x8) {
  size_t dim1 = 10;
  size_t dim2 = 9;
  size_t dim3 = 8;

  std::vector<std::vector<int64_t>> my_mat_a(dim1, std::vector<int64_t>(dim2));
  std::vector<std::vector<int64_t>> my_mat_b(dim2, std::vector<int64_t>(dim3));

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, 10);
  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++) my_mat_a[i][j] = distrib(gen);
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_mat_b[i][j] = distrib(gen);

  std::vector<std::vector<int64_t>> out =
      testMatMulRow(my_mat_a, my_mat_b, dim1, dim2, dim3);

  std::vector<std::vector<int64_t>> expected_out(dim1,
                                                 std::vector<int64_t>(dim3));
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        expected_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }
  checkEqual(expected_out, out);
}

TEST(palisade_bfv_kernel_executor, MatMulRow4x3x2) {
  size_t dim1 = 4;
  size_t dim2 = 3;
  size_t dim3 = 2;

  // Row-major
  std::vector<std::vector<int64_t>> my_mat_a{
      {1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}};
  std::vector<std::vector<int64_t>> my_mat_b{{1, 2}, {3, 4}, {5, 6}};

  //  Row-major
  std::vector<std::vector<int64_t>> expected_out{
      {22, 28}, {49, 64}, {76, 100}, {103, 136}};

  std::vector<std::vector<int64_t>> out =
      testMatMulRow(my_mat_a, my_mat_b, dim1, dim2, dim3);

  checkEqual(out, expected_out);
}

}  // namespace palisade
}  // namespace he
}  // namespace intel
