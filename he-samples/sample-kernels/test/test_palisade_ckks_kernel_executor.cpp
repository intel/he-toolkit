// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <algorithm>
#include <memory>
#include <numeric>
#include <vector>

#include "kernels/palisade/palisade_ckks_kernel_executor.h"
#include "kernels/palisade/palisade_util.h"
#include "test_util.h"

namespace intel {
namespace he {
namespace palisade {

std::vector<double> testDotCipherBatchAxis(const std::vector<double>& input1,
                                           const std::vector<double>& input2,
                                           size_t dim1, size_t dim2,
                                           size_t dim3) {
  auto cc = generatePalisadeCKKSContext(8192, std::vector<int>(3, 60));

  size_t batch_size = 1;

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(
      cc, keys.publicKey, lbcrypto::RescalingTechnique::APPROXAUTO);

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg2(dim2 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain =
        cc->MakeCKKSPackedPlaintext(std::vector<double>{input1[i]});
    arg1[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    lbcrypto::Plaintext plain =
        cc->MakeCKKSPackedPlaintext(std::vector<double>{input2[i]});
    arg2[i] = cc->Encrypt(keys.publicKey, plain);
  }

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_out =
      kernel_executor.dotCipherBatchAxis(arg1, arg2, dim1, dim2, dim3);

  std::vector<double> plain_out;
  for (const auto& cipher : cipher_out) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, cipher, &result);
    plain_out.push_back(result->GetRealPackedValue()[0]);
  }
  return plain_out;
}

std::vector<double> testDotPlainBatchAxis(const std::vector<double>& input1,
                                          const std::vector<double>& input2,
                                          size_t dim1, size_t dim2,
                                          size_t dim3) {
  auto cc = generatePalisadeCKKSContext(8192, std::vector<int>(4, 60));

  size_t batch_size = 1;

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(
      cc, keys.publicKey, lbcrypto::RescalingTechnique::APPROXAUTO);

  // Matrixes in column-major form
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> arg1(dim1 * dim2);
  std::vector<lbcrypto::Plaintext> arg2(dim2 * dim3);

  // Initialize args
  for (size_t i = 0; i < arg1.size(); ++i) {
    lbcrypto::Plaintext plain =
        cc->MakeCKKSPackedPlaintext(std::vector<double>{input1[i]});
    arg1[i] = cc->Encrypt(keys.publicKey, plain);
  }

  for (size_t i = 0; i < arg2.size(); ++i) {
    arg2[i] = cc->MakeCKKSPackedPlaintext(std::vector<double>{input2[i]});
  }

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_out =
      kernel_executor.dotPlainBatchAxis(arg1, arg2, dim1, dim2, dim3);

  std::vector<double> plain_out;
  for (const auto& cipher : cipher_out) {
    lbcrypto::Plaintext result;
    cc->Decrypt(keys.secretKey, cipher, &result);
    plain_out.push_back(result->GetRealPackedValue()[0]);
  }
  return plain_out;
}

std::vector<std::vector<double>> testMatMulEIP(
    const std::vector<std::vector<double>>& my_mat_a,
    const std::vector<std::vector<double>>& my_trans_b, size_t dim1,
    size_t dim2, size_t dim3) {
  size_t poly_mod = 4096;
  auto cc = generatePalisadeCKKSContext(poly_mod, std::vector<int>(4));
  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);

  // For Each Row in A
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(my_mat_a[i]);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(my_trans_b[i]);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // One Ciphertext for each value in the resulting matrix
  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> sum(
      dim1, std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>(dim3));

  sum = kernel_executor.matMulEIP(cipher_a, cipher_b, dim1, dim2, dim3, dim2);

  std::vector<std::vector<lbcrypto::Plaintext>> sum_plain(
      dim1, std::vector<lbcrypto::Plaintext>(dim3));
  std::vector<std::vector<double>> ret_mat_he(dim1, std::vector<double>(dim3));

  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      cc->Decrypt(keys.secretKey, sum[i][j], &sum_plain[i][j]);
      ret_mat_he[i][j] = sum_plain[i][j]->GetRealPackedValue()[0];
    }
  }
  return ret_mat_he;
}

std::vector<std::vector<double>> testMatMulVal(
    const std::vector<std::vector<double>>& my_mat_a,
    const std::vector<std::vector<double>>& my_trans_b, size_t dim1,
    size_t dim2, size_t dim3) {
  int poly_modulus_degree = 4096;
  auto cc =
      generatePalisadeCKKSContext(poly_modulus_degree, std::vector<int>(4));
  std::vector<int32_t> vec(dim2);
  std::iota(std::begin(vec), std::end(vec), 1);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);
  PalisadeCKKSKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_a(dim1);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_b(dim3);

  // For Each Row in A
  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(my_mat_a[i]);
    cipher_a[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // For Each Column in B (Row in tB)
  for (size_t i = 0; i < dim3; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(my_trans_b[i]);
    cipher_b[i] = cc->Encrypt(keys.publicKey, plain);
  }

  // One Ciphertext for each value in the resulting matrix
  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> sum =
      kernel_executor.matMulVal(cipher_a, cipher_b, dim1, dim2, dim3);

  std::vector<std::vector<double>> ret_mat_he(dim1, std::vector<double>(dim3));
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      lbcrypto::Plaintext sum_plain;
      cc->Decrypt(keys.secretKey, sum[i][j], &sum_plain);
      ret_mat_he[i][j] = sum_plain->GetRealPackedValue()[0];
    }
  }
  return ret_mat_he;
}

std::vector<std::vector<double>> testMatMulRow(
    const std::vector<std::vector<double>>& my_mat_a,
    const std::vector<std::vector<double>>& my_mat_b, size_t dim1, size_t dim2,
    size_t dim3) {
  int poly_modulus_degree = 4096;
  int slots = poly_modulus_degree / 2;
  auto cc =
      generatePalisadeCKKSContext(poly_modulus_degree, std::vector<int>(4));

  int64_t spacers = slots / dim2;

  std::vector<int32_t> vec(dim2);
  int n = 0;
  std::generate(std::begin(vec), std::end(vec),
                [&n, &spacers] { return n += spacers; });

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, vec);
  cc->EvalSumKeyGen(keys.secretKey);

  PalisadeCKKSKernelExecutor kernel_executor(cc, keys.publicKey);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> vec_cipher_a(dim1);

  std::vector<double> vec_a(slots, 0);
  std::vector<double> vec_b(slots, 0);
  std::vector<std::vector<double>> vec_container_a(dim1);

  for (size_t i = 0; i < dim1; i++) {
#pragma omp parallel for collapse(2)
    for (size_t j = 0; j < dim2; j++) {
      for (size_t k = 0; k < dim3; k++) {
        vec_a[spacers * j + k] = my_mat_a[i][j];
        if (i == 0) {
          vec_b[spacers * j + k] = my_mat_b[j][k];
        }
      }
    }
    vec_container_a[i] = vec_a;
  }

  for (size_t i = 0; i < dim1; i++) {
    lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(vec_container_a[i]);
    auto cipher = cc->Encrypt(keys.publicKey, plain);
    vec_cipher_a[i] = cipher;
  }
  lbcrypto::Plaintext plain = cc->MakeCKKSPackedPlaintext(vec_b);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_b =
      cc->Encrypt(keys.publicKey, plain);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> sum =
      kernel_executor.matMulRow(vec_cipher_a, cipher_b, dim1, dim2, dim3,
                                slots);

  std::vector<std::vector<double>> vec_ct_res(sum.size());
  std::vector<std::vector<double>> vec_ct_res2(sum.size());
#pragma omp parallel for
  for (size_t i = 0; i < sum.size(); i++) {
    lbcrypto::Plaintext sum_plain;
    cc->Decrypt(keys.secretKey, sum[i], &sum_plain);
    vec_ct_res2[i] = sum_plain->GetRealPackedValue();
    vec_ct_res2[i].resize(dim3);
  }
  for (size_t i = 0; i < vec_ct_res2.size(); i++) {
    for (size_t j = 0; j < vec_ct_res2[i].size(); j++) {
      vec_ct_res[i].push_back(vec_ct_res2[i][j]);
    }
  }
  return vec_ct_res;
}

void prepareLinearRegression4x3(double& bias, std::vector<double>& weights,
                                std::vector<std::vector<double>>& inputs,
                                std::vector<double>& ground_truth) {
  // values hand-picked to ensure that sigmoid input remains between -1 and 1
  // to ensure valid domain range for polynomial approximation
  bias = -0.463;
  weights.assign({0.438, -0.18, 0.0, 0.3141592654});
  inputs.resize(3);
  inputs[0].assign({0.7232, -0.3469, 0.7383, 0.6038});
  inputs[1].assign({-0.8509, -0.8242, -0.1463, -0.3124});
  inputs[2].assign({0.6432, 0.0438, 0.9413, 0.2812});
  for (std::size_t i = 0; i < inputs.size(); ++i)
    ground_truth.emplace_back(std::inner_product(
        inputs[i].begin(), inputs[i].end(), weights.begin(), bias));
}

void prepareLogisticRegression4x3(double& bias, std::vector<double>& weights,
                                  std::vector<std::vector<double>>& inputs,
                                  std::vector<double>& ground_truth) {
  prepareLinearRegression4x3(bias, weights, inputs, ground_truth);
  std::transform(ground_truth.begin(), ground_truth.end(), ground_truth.begin(),
                 approxSigmoid<3>);
}

std::vector<double> testLogisticRegression4x3(
    double bias, const std::vector<double>& weights,
    const std::vector<std::vector<double>>& inputs,
    std::size_t sigmoid_degree) {
  std::uint32_t batch_size = weights.size();
  std::uint32_t mult_depth = 5;
  std::uint32_t scale_factor_bits = 45;
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

  std::vector<int32_t> il(inputs.size());
  for (int32_t i = 0; i < il.size(); ++i) il[i] = -i - 1;
  cc->EvalAtIndexKeyGen(key_pair.secretKey, il);
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> cipher_inputs;
  cipher_inputs.reserve(inputs.size());
  lbcrypto::Plaintext tmp_plain;
  for (size_t i = 0; i < inputs.size(); ++i)
    cipher_inputs.push_back(cc->Encrypt(
        key_pair.publicKey, cc->MakeCKKSPackedPlaintext(inputs[i])));
  tmp_plain = cc->MakeCKKSPackedPlaintext(weights);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_weights =
      cc->Encrypt(key_pair.publicKey, tmp_plain);
  std::vector<double> tmp_bias(inputs.size());
  std::fill(tmp_bias.begin(), tmp_bias.end(), bias);
  tmp_plain = cc->MakeCKKSPackedPlaintext(tmp_bias);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_bias =
      cc->Encrypt(key_pair.publicKey, tmp_plain);

  PalisadeCKKSKernelExecutor kernel_executor(cc, key_pair.publicKey, rs_tech);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& cipher_result = cipher_weights;
  cipher_result = kernel_executor.evaluateLogisticRegression(
      cipher_weights, cipher_inputs, cipher_bias, weights.size(),
      sigmoid_degree);

  cc->Decrypt(key_pair.secretKey, cipher_result, &tmp_plain);
  std::vector<double> retval = tmp_plain->GetRealPackedValue();
  retval.resize(inputs.size());
  return retval;
}

TEST(palisade_ckks_kernel_executor, dotPlainBatchAxis2x2x2) {
  std::vector<double> input1{1, 2, 3, 4};
  std::vector<double> input2{1, 2, 3, 4};
  std::vector<double> exp_out{7, 10, 15, 22};

  std::vector<double> out = testDotPlainBatchAxis(input1, input2, 2, 2, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_ckks_kernel_executor, dotPlainBatchAxis4x3x2) {
  std::vector<double> input1{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<double> input2{1, 2, 3, 4, 5, 6};
  std::vector<double> exp_out{38, 44, 50, 56, 83, 98, 113, 128};

  std::vector<double> out = testDotPlainBatchAxis(input1, input2, 4, 3, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_ckks_kernel_executor, dotCipherBatchAxis2x2x2) {
  std::vector<double> input1{1, 2, 3, 4};
  std::vector<double> input2{1, 2, 3, 4};
  std::vector<double> exp_out{7, 10, 15, 22};

  std::vector<double> out = testDotCipherBatchAxis(input1, input2, 2, 2, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_ckks_kernel_executor, dotCipherBatchAxis4x3x2) {
  std::vector<double> input1{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<double> input2{1, 2, 3, 4, 5, 6};
  std::vector<double> exp_out{38, 44, 50, 56, 83, 98, 113, 128};

  std::vector<double> out = testDotCipherBatchAxis(input1, input2, 4, 3, 2);

  checkEqual(out, exp_out);
}

TEST(palisade_ckks_kernel_executor, MatMulEIP10x9x8) {
  size_t dim1 = 10;
  size_t dim2 = 9;
  size_t dim3 = 8;

  std::vector<std::vector<double>> my_mat_a(dim1, std::vector<double>(dim2));
  std::vector<std::vector<double>> my_mat_b(dim2, std::vector<double>(dim3));
  std::vector<std::vector<double>> my_trans_b(dim3, std::vector<double>(dim2));

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, 10);
  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++)
      my_mat_a[i][j] = static_cast<double>(distrib(gen));
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++)
      my_mat_b[i][j] = static_cast<double>(distrib(gen));

#pragma omp parallel for collapse(2)
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_trans_b[j][i] = my_mat_b[i][j];

  std::vector<std::vector<double>> out =
      testMatMulEIP(my_mat_a, my_trans_b, dim1, dim2, dim3);

  std::vector<std::vector<double>> expected_out(dim1,
                                                std::vector<double>(dim3));

  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        expected_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }
  checkEqual(out, expected_out);
}

TEST(palisade_ckks_kernel_executor, MatMulEIP4x3x2) {
  size_t dim1 = 4;
  size_t dim2 = 3;
  size_t dim3 = 2;

  // Row-major
  std::vector<std::vector<double>> my_mat_a{
      {1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}};
  std::vector<std::vector<double>> my_trans_b{{1, 3, 5}, {2, 4, 6}};

  //  Row-major
  std::vector<std::vector<double>> expected_out{
      {22, 28}, {49, 64}, {76, 100}, {103, 136}};

  std::vector<std::vector<double>> out =
      testMatMulEIP(my_mat_a, my_trans_b, dim1, dim2, dim3);

  checkEqual(out, expected_out);
}

TEST(palisade_ckks_kernel_executor, MatMulVal10x9x8) {
  size_t dim1 = 10;
  size_t dim2 = 9;
  size_t dim3 = 8;

  std::vector<std::vector<double>> my_mat_a(dim1, std::vector<double>(dim2));
  std::vector<std::vector<double>> my_mat_b(dim2, std::vector<double>(dim3));
  std::vector<std::vector<double>> my_trans_b(dim3, std::vector<double>(dim2));

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution distrib(0, 10);
  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++)
      my_mat_a[i][j] = static_cast<double>(distrib(gen));
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++)
      my_mat_b[i][j] = static_cast<double>(distrib(gen));

  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_trans_b[j][i] = my_mat_b[i][j];

  std::vector<std::vector<double>> out =
      testMatMulVal(my_mat_a, my_trans_b, dim1, dim2, dim3);

  std::vector<std::vector<double>> expected_out(dim1,
                                                std::vector<double>(dim3));
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        expected_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }
  checkEqual(expected_out, out);
}

TEST(palisade_ckks_kernel_executor, MatMulVal4x3x2) {
  size_t dim1 = 4;
  size_t dim2 = 3;
  size_t dim3 = 2;

  // Row-major
  std::vector<std::vector<double>> my_mat_a{
      {1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}};
  std::vector<std::vector<double>> my_trans_b{{1, 3, 5}, {2, 4, 6}};

  //  Row-major
  std::vector<std::vector<double>> expected_out{
      {22, 28}, {49, 64}, {76, 100}, {103, 136}};

  std::vector<std::vector<double>> out =
      testMatMulVal(my_mat_a, my_trans_b, dim1, dim2, dim3);

  checkEqual(out, expected_out);
}

TEST(palisade_ckks_kernel_executor, MatMulRow10x9x8) {
  size_t dim1 = 10;
  size_t dim2 = 9;
  size_t dim3 = 8;

  std::vector<std::vector<double>> my_mat_a(dim1, std::vector<double>(dim2));
  std::vector<std::vector<double>> my_mat_b(dim2, std::vector<double>(dim3));

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, 10);
  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++)
      my_mat_a[i][j] = static_cast<double>(distrib(gen));
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++)
      my_mat_b[i][j] = static_cast<double>(distrib(gen));

  std::vector<std::vector<double>> out =
      testMatMulRow(my_mat_a, my_mat_b, dim1, dim2, dim3);

  std::vector<std::vector<double>> expected_out(dim1,
                                                std::vector<double>(dim3));
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        expected_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }
  checkEqual(expected_out, out);
}

TEST(palisade_ckks_kernel_executor, MatMulRow4x3x2) {
  size_t dim1 = 4;
  size_t dim2 = 3;
  size_t dim3 = 2;

  // Row-major
  std::vector<std::vector<double>> my_mat_a{
      {1, 2, 3}, {4, 5, 6}, {7, 8, 9}, {10, 11, 12}};
  std::vector<std::vector<double>> my_mat_b{{1, 2}, {3, 4}, {5, 6}};

  //  Row-major
  std::vector<std::vector<double>> expected_out{
      {22, 28}, {49, 64}, {76, 100}, {103, 136}};

  std::vector<std::vector<double>> out =
      testMatMulRow(my_mat_a, my_mat_b, dim1, dim2, dim3);

  checkEqual(out, expected_out);
}

TEST(palisade_ckks_kernel_executor, logisticRegression4x3_SigDeg3) {
  constexpr unsigned int sigmoid_deg = 3;
  double bias;
  std::vector<double> weights;
  std::vector<std::vector<double>> inputs;
  std::vector<double> ground_truth;
  prepareLogisticRegression4x3(bias, weights, inputs, ground_truth);
  std::vector<double> output =
      testLogisticRegression4x3(bias, weights, inputs, sigmoid_deg);

  checkEqual(output, ground_truth);
}

}  // namespace palisade
}  // namespace he
}  // namespace intel
