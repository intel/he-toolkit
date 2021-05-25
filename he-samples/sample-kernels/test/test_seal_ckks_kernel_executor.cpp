// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>
#include <seal/seal.h>

#include <algorithm>
#include <memory>
#include <numeric>
#include <vector>

#include "kernels/seal/seal_ckks_context.h"
#include "kernels/seal/seal_ckks_kernel_executor.h"
#include "test_util.h"

namespace intel {
namespace he {
namespace heseal {

std::vector<double> testDotCipherBatchAxis(const std::vector<double>& inputA,
                                           const std::vector<double>& inputB,
                                           size_t dim1, size_t dim2,
                                           size_t dim3) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  size_t batch_size = 1;

  std::vector<seal::Ciphertext> ciphersA =
      context.encryptVector(inputA, batch_size);

  std::vector<seal::Ciphertext> ciphersB =
      context.encryptVector(inputB, batch_size);

  std::vector<seal::Ciphertext> cipher_dot =
      kernel_executor.dotCipherBatchAxis(ciphersA, ciphersB, dim1, dim2, dim3);

  std::vector<seal::Plaintext> decrypted = context.decryptVector(cipher_dot);
  return context.decodeVector(decrypted, batch_size);
}

std::vector<double> testDotPlainBatchAxis(const std::vector<double>& inputA,
                                          const std::vector<double>& inputB,
                                          size_t dim1, size_t dim2,
                                          size_t dim3) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  size_t batch_size = 1;

  std::vector<seal::Ciphertext> ciphersA =
      context.encryptVector(inputA, batch_size);

  std::vector<seal::Plaintext> plainsB =
      context.encodeVector(inputB, batch_size);

  std::vector<seal::Ciphertext> cipher_dot =
      kernel_executor.dotPlainBatchAxis(ciphersA, plainsB, dim1, dim2, dim3);

  std::vector<seal::Plaintext> decrypted = context.decryptVector(cipher_dot);
  return context.decodeVector(decrypted, batch_size);
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
  for (std::size_t i = 0; i < inputs.size(); ++i) {
    ground_truth.emplace_back(std::inner_product(
        inputs[i].begin(), inputs[i].end(), weights.begin(), bias));
  }
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
  SealCKKSContext context(1UL << 14, {60, 45, 45, 45, 45, 45}, 1UL << 45, true,
                          true);
  SealCKKSKernelExecutor kernel_executor(context);
  seal::Plaintext plain_bias;
  seal::Ciphertext cipher_bias;
  context.encoder().encode(bias, context.scale(), plain_bias);
  context.encryptor().encrypt(plain_bias, cipher_bias);
  std::vector<seal::Ciphertext> cipher_weights = context.encryptVector(weights);
  std::vector<std::vector<seal::Ciphertext>> cipher_inputs(inputs.size());
  for (std::size_t i = 0; i < inputs.size(); ++i)
    cipher_inputs[i] = context.encryptVector(inputs[i]);
  std::vector<seal::Ciphertext> cipher_retval =
      kernel_executor.evaluateLogisticRegression(cipher_weights, cipher_inputs,
                                                 cipher_bias, weights.size(),
                                                 sigmoid_degree);
  std::vector<double> retval =
      context.decodeVector(context.decryptVector(cipher_retval));
  retval.resize(inputs.size());
  return retval;
}

TEST(seal_ckks_kernel_executor, encode_vector) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);

  size_t num_plaintexts = 7;
  size_t batch_size = context.encoder().slot_count();

  std::vector<double> input(num_plaintexts * batch_size);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<double>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), batch_size);

  ASSERT_EQ(encoded.size(), num_plaintexts);

  std::vector<double> output;
  for (size_t i = 0; i < num_plaintexts; ++i) {
    std::vector<double> decoded;
    context.encoder().decode(encoded[i], decoded);
    output.insert(output.end(), decoded.begin(), decoded.end());
  }

  checkEqual(output, input);
}

TEST(seal_ckks_kernel_executor, encode_vector_batch_size_1) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);

  size_t num_plaintexts = 7;
  size_t batch_size = 1;

  std::vector<double> input(num_plaintexts * batch_size);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<double>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), batch_size);

  ASSERT_EQ(encoded.size(), num_plaintexts);

  std::vector<double> output;
  for (size_t i = 0; i < num_plaintexts; ++i) {
    std::vector<double> decoded;
    context.encoder().decode(encoded[i], decoded);
    decoded.resize(batch_size);
    output.insert(output.end(), decoded.begin(), decoded.end());
  }
  checkEqual(output, input);
}

TEST(seal_ckks_kernel_executor, encode_vector_batch_size_3) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);

  size_t num_plaintexts = 4;
  size_t batch_size = 3;

  std::vector<double> input(10);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<double>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), batch_size);

  ASSERT_EQ(encoded.size(), num_plaintexts);

  std::vector<double> output;
  for (size_t i = 0; i < num_plaintexts; ++i) {
    std::vector<double> decoded;
    context.encoder().decode(encoded[i], decoded);
    if (i == num_plaintexts - 1) {
      size_t last_batch_size = input.size() % batch_size;
      decoded.resize(1);
    } else {
      decoded.resize(batch_size);
    }
    output.insert(output.end(), decoded.begin(), decoded.end());
  }
  checkEqual(output, input);
}

TEST(seal_ckks_kernel_executor, decode_vector) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);

  size_t num_plaintexts = 7;
  size_t slot_count = context.encoder().slot_count();

  std::vector<double> input(num_plaintexts * slot_count);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<double>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), slot_count);
  std::vector<double> decoded = context.decodeVector(encoded, slot_count);

  checkEqual(input, decoded);
}

TEST(seal_ckks_kernel_executor, encrypt_vector) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);

  size_t num_plaintexts = 7;
  size_t slot_count = context.encoder().slot_count();

  std::vector<double> input(num_plaintexts * slot_count);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<double>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), slot_count);
  std::vector<seal::Ciphertext> encrypted = context.encryptVector(encoded);

  ASSERT_EQ(encrypted.size(), encoded.size());

  for (size_t i = 0; i < encrypted.size(); ++i) {
    seal::Plaintext plain;
    context.decryptor().decrypt(encrypted[i], plain);

    std::vector<double> decrypted_decoded;
    context.encoder().decode(plain, decrypted_decoded);

    std::vector<double> decoded;
    context.encoder().decode(encoded[i], decoded);

    checkEqual(decoded, decrypted_decoded);
  }
}

TEST(seal_ckks_kernel_executor, decrypt_vector) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);

  size_t num_plaintexts = 7;
  size_t slot_count = context.encoder().slot_count();

  std::vector<double> input(num_plaintexts * slot_count);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<double>(i);
  }

  std::vector<seal::Ciphertext> encrypted =
      context.encryptVector(gsl::span(input.data(), input.size()), slot_count);

  std::vector<seal::Plaintext> decrypted = context.decryptVector(encrypted);
  std::vector<double> decoded = context.decodeVector(decrypted, slot_count);

  checkEqual(input, decoded);
}

TEST(seal_ckks_kernel_executor, level) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> input{0.1, 0.2, 0.3, 0.4};
  seal::Plaintext plain;

  context.encoder().encode(input, context.scale(), plain);

  seal::Ciphertext cipher1;
  context.encryptor().encrypt(plain, cipher1);
  seal::Ciphertext cipher2;
  context.encryptor().encrypt(plain, cipher2);

  EXPECT_EQ(kernel_executor.getLevel(plain), 2);
  EXPECT_EQ(kernel_executor.getLevel(cipher1), 2);

  kernel_executor.getEvaluator()->rescale_to_next_inplace(cipher1);
  EXPECT_EQ(kernel_executor.getLevel(cipher1), 1);

  kernel_executor.matchLevel(&cipher1, &cipher2);
  EXPECT_EQ(kernel_executor.getLevel(cipher1), 1);
  EXPECT_EQ(kernel_executor.getLevel(cipher2), 1);

  kernel_executor.matchLevel(&cipher1, &cipher2);
  EXPECT_EQ(kernel_executor.getLevel(cipher1), 1);
  EXPECT_EQ(kernel_executor.getLevel(cipher2), 1);

  kernel_executor.getEvaluator()->mod_switch_to_next_inplace(cipher2);
  EXPECT_EQ(kernel_executor.getLevel(cipher2), 0);

  kernel_executor.matchLevel(&cipher1, &cipher2);
  EXPECT_EQ(kernel_executor.getLevel(cipher1), 0);
  EXPECT_EQ(kernel_executor.getLevel(cipher2), 0);
}

TEST(seal_ckks_kernel_executor, add) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40, false, false);
  SealCKKSKernelExecutor kernel_executor(context);

  size_t num_plaintexts = 7;
  size_t slot_count = context.encoder().slot_count();

  std::vector<double> inputA(num_plaintexts * slot_count);
  std::vector<double> inputB(num_plaintexts * slot_count);
  std::vector<double> expected_out(num_plaintexts * slot_count);
  for (size_t i = 0; i < inputA.size(); ++i) {
    inputA[i] = static_cast<double>(i);
    inputB[i] = static_cast<double>(2 * i + 1);
    expected_out[i] = inputA[i] + inputB[i];
  }

  std::vector<seal::Ciphertext> cipherA = context.encryptVector(
      gsl::span(inputA.data(), inputA.size()), slot_count);

  std::vector<seal::Ciphertext> cipherB = context.encryptVector(
      gsl::span(inputB.data(), inputB.size()), slot_count);

  std::vector<seal::Ciphertext> cipher_sum =
      kernel_executor.add(cipherA, cipherB);
  std::vector<seal::Plaintext> plain_sum = context.decryptVector(cipher_sum);

  std::vector<double> output = context.decodeVector(plain_sum, slot_count);
  checkEqual(output, expected_out);
}

TEST(seal_ckks_kernel_executor, accumulate) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> input{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};

  std::vector<seal::Ciphertext> ciphers =
      context.encryptVector(gsl::span(input.data(), input.size()));

  seal::Ciphertext cipher_sum =
      kernel_executor.accumulate(ciphers, input.size());

  seal::Plaintext plain_sum;
  context.decryptor().decrypt(cipher_sum, plain_sum);
  std::vector<double> output;
  context.encoder().decode(plain_sum, output);

  ASSERT_NEAR(output[0], 78, 0.01);
}

TEST(seal_ckks_kernel_executor, dot) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> inputA{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<double> inputB{12, 11, 10, 9, 5, 6, 7, 8, 9, 10, 11, 12};

  std::vector<seal::Ciphertext> ciphersA =
      context.encryptVector(gsl::span(inputA.data(), inputA.size()));

  std::vector<seal::Ciphertext> ciphersB =
      context.encryptVector(gsl::span(inputB.data(), inputB.size()));

  seal::Ciphertext cipher_dot =
      kernel_executor.dot(ciphersA, ciphersB, inputA.size());

  seal::Plaintext plain_dot;
  context.decryptor().decrypt(cipher_dot, plain_dot);
  std::vector<double> output;
  context.encoder().decode(plain_dot, output);

  ASSERT_NEAR(output[0], 720, 0.01);
}

TEST(seal_ckks_kernel_executor, matMul) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<std::vector<double>> mat_A{
      {1, -2, 3, -4}, {-5, 6, -7, 8}, {9, -10, 11, -12}};
  std::vector<std::vector<double>> mat_B_T{{21, -23, 25, 27},
                                           {-22, 24, -26, -28}};
  std::vector<double> exp_out{34, -36, -202, 212, 370, -388};
  std::vector<double> output;

  std::vector<std::vector<seal::Ciphertext>> cipher_A(mat_A.size());
  std::vector<std::vector<seal::Ciphertext>> cipher_B_T(mat_B_T.size());
  for (std::size_t r = 0; r < mat_A.size(); ++r)
    cipher_A[r] = context.encryptVector(mat_A[r]);
  for (std::size_t r = 0; r < mat_B_T.size(); ++r)
    cipher_B_T[r] = context.encryptVector(mat_B_T[r]);

  auto cipher_AB =
      kernel_executor.matMul(cipher_A, cipher_B_T, mat_A.front().size());

  output.resize(cipher_AB.size());
  for (std::size_t i = 0; i < output.size(); ++i) {
    std::vector<double> tmp;
    seal::Plaintext plain;
    context.decryptor().decrypt(cipher_AB[i], plain);
    context.encoder().decode(plain, tmp);
    output[i] = tmp.front();
  }

  checkEqual(output, exp_out);
}

TEST(seal_ckks_kernel_executor, logisticRegression4x3_SigDeg3) {
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

TEST(seal_ckks_kernel_executor, dotCipherBatchAxis4x3x2) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> inputA{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<double> inputB{1, 2, 3, 4, 5, 6};
  std::vector<double> exp_out{38, 44, 50, 56, 83, 98, 113, 128};
  std::vector<double> output = testDotCipherBatchAxis(inputA, inputB, 4, 3, 2);

  checkEqual(output, exp_out);
}

TEST(seal_ckks_kernel_executor, DotCipherBatchAxis2x2x2) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> input1{1, 2, 3, 4};
  std::vector<double> input2{1, 2, 3, 4};
  std::vector<double> exp_out{7, 10, 15, 22};
  std::vector<double> output = testDotCipherBatchAxis(input1, input2, 2, 2, 2);

  checkEqual(output, exp_out);
}

TEST(seal_ckks_kernel_executor, DotPlainBatchAxis4x3x2) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> inputA{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<double> inputB{1, 2, 3, 4, 5, 6};
  std::vector<double> exp_out{38, 44, 50, 56, 83, 98, 113, 128};
  std::vector<double> output = testDotCipherBatchAxis(inputA, inputB, 4, 3, 2);

  checkEqual(output, exp_out);
}

TEST(seal_ckks_kernel_executor, DotPlainBatchAxis2x2x2) {
  SealCKKSContext context(8192, {60, 40, 40}, 1UL << 40);
  SealCKKSKernelExecutor kernel_executor(context);

  std::vector<double> input1{1, 2, 3, 4};
  std::vector<double> input2{1, 2, 3, 4};
  std::vector<double> exp_out{7, 10, 15, 22};
  std::vector<double> output = testDotPlainBatchAxis(input1, input2, 2, 2, 2);

  checkEqual(output, exp_out);
}

}  // namespace heseal
}  // namespace he
}  // namespace intel
