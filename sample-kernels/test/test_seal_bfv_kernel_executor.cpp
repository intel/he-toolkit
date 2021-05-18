// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>
#include <seal/seal.h>

#include <memory>
#include <vector>

#include "kernels/seal/seal_bfv_context.h"
#include "kernels/seal/seal_bfv_kernel_executor.h"
#include "test_util.h"

namespace intel {
namespace he {
namespace heseal {

TEST(seal_bfv_kernel_executor, encode_vector) {
  SealBFVContext context(8192, {60, 40, 40}, false, false);

  size_t num_plaintexts = 7;
  size_t batch_size = context.batch_encoder().slot_count();

  std::vector<uint64_t> input(num_plaintexts * batch_size);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<uint64_t>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), batch_size);

  ASSERT_EQ(encoded.size(), num_plaintexts);

  std::vector<uint64_t> output;
  for (size_t i = 0; i < num_plaintexts; ++i) {
    std::vector<uint64_t> decoded;
    context.batch_encoder().decode(encoded[i], decoded);
    output.insert(output.end(), decoded.begin(), decoded.end());
  }

  checkEqual(output, input);
}

TEST(seal_bfv_kernel_executor, encode_vector_batch_size_1) {
  SealBFVContext context(8192, {60, 40, 40}, false, false);

  size_t num_plaintexts = 7;
  size_t batch_size = 1;

  std::vector<uint64_t> input(num_plaintexts * batch_size);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<uint64_t>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), batch_size);

  ASSERT_EQ(encoded.size(), num_plaintexts);

  std::vector<uint64_t> output;
  for (size_t i = 0; i < num_plaintexts; ++i) {
    std::vector<uint64_t> decoded;
    context.batch_encoder().decode(encoded[i], decoded);
    decoded.resize(batch_size);
    output.insert(output.end(), decoded.begin(), decoded.end());
  }
  checkEqual(output, input);
}

TEST(seal_bfv_kernel_executor, encode_vector_batch_size_3) {
  SealBFVContext context(8192, {60, 40, 40}, false, false);

  size_t num_plaintexts = 4;
  size_t batch_size = 3;

  std::vector<uint64_t> input(10);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<uint64_t>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), batch_size);

  ASSERT_EQ(encoded.size(), num_plaintexts);

  std::vector<uint64_t> output;
  for (size_t i = 0; i < num_plaintexts; ++i) {
    std::vector<uint64_t> decoded;
    context.batch_encoder().decode(encoded[i], decoded);
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

TEST(seal_bfv_kernel_executor, decode_vector) {
  SealBFVContext context(8192, {60, 40, 40}, false, false);

  size_t num_plaintexts = 7;
  size_t slot_count = context.batch_encoder().slot_count();

  std::vector<uint64_t> input(num_plaintexts * slot_count);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<uint64_t>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), slot_count);
  std::vector<uint64_t> decoded = context.decodeVector(encoded, slot_count);

  checkEqual(input, decoded);
}

TEST(seal_bfv_kernel_executor, encrypt_vector) {
  SealBFVContext context(8192, {60, 40, 40}, false, false);

  size_t num_plaintexts = 7;
  size_t slot_count = context.batch_encoder().slot_count();

  std::vector<uint64_t> input(num_plaintexts * slot_count);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<uint64_t>(i);
  }

  std::vector<seal::Plaintext> encoded =
      context.encodeVector(gsl::span(input.data(), input.size()), slot_count);
  std::vector<seal::Ciphertext> encrypted = context.encryptVector(encoded);

  ASSERT_EQ(encrypted.size(), encoded.size());

  for (size_t i = 0; i < encrypted.size(); ++i) {
    seal::Plaintext plain;
    context.decryptor().decrypt(encrypted[i], plain);

    std::vector<uint64_t> decrypted_decoded;
    context.batch_encoder().decode(plain, decrypted_decoded);

    std::vector<uint64_t> decoded;
    context.batch_encoder().decode(encoded[i], decoded);

    checkEqual(decoded, decrypted_decoded);
  }
}

TEST(seal_bfv_kernel_executor, decrypt_vector) {
  SealBFVContext context(8192, {60, 40, 40}, false, false);

  size_t num_plaintexts = 7;
  size_t slot_count = context.batch_encoder().slot_count();

  std::vector<uint64_t> input(num_plaintexts * slot_count);
  for (size_t i = 0; i < input.size(); ++i) {
    input[i] = static_cast<uint64_t>(i);
  }

  std::vector<seal::Ciphertext> encrypted =
      context.encryptVector(gsl::span(input.data(), input.size()), slot_count);

  std::vector<seal::Plaintext> decrypted = context.decryptVector(encrypted);
  std::vector<uint64_t> decoded = context.decodeVector(decrypted, slot_count);

  checkEqual(input, decoded);
}

TEST(seal_bfv_kernel_executor, dotCipherBatchAxis4x3x2) {
  SealBFVContext context(8192, std::vector<int>(3, 50), true, true);
  SealBFVKernelExecutor kernel_executor(context);

  size_t num_plaintexts = 3;
  size_t batch_size = 1;
  size_t slot_count = context.batch_encoder().slot_count();

  std::vector<uint64_t> inputA{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<uint64_t> inputB{1, 2, 3, 4, 5, 6};
  std::vector<uint64_t> exp_out{38, 44, 50, 56, 83, 98, 113, 128};

  std::vector<seal::Ciphertext> ciphersA =
      context.encryptVector(inputA, batch_size);

  std::vector<seal::Ciphertext> ciphersB =
      context.encryptVector(inputB, batch_size);

  std::vector<seal::Ciphertext> cipher_dot =
      kernel_executor.dotCipherBatchAxis(ciphersA, ciphersB, 4, 3, 2);

  std::vector<seal::Plaintext> decrypted = context.decryptVector(cipher_dot);
  std::vector<uint64_t> output = context.decodeVector(decrypted, batch_size);

  checkEqual(output, exp_out);
}

TEST(seal_bfv_kernel_executor, DotPlainBatchAxis4x3x2) {
  SealBFVContext context(8192, std::vector<int>(3, 50), true, true);
  SealBFVKernelExecutor kernel_executor(context);

  size_t num_plaintexts = 3;
  size_t batch_size = 1;
  size_t slot_count = context.batch_encoder().slot_count();

  std::vector<uint64_t> inputA{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
  std::vector<uint64_t> inputB{1, 2, 3, 4, 5, 6};
  std::vector<uint64_t> exp_out{38, 44, 50, 56, 83, 98, 113, 128};

  std::vector<seal::Ciphertext> ciphersA =
      context.encryptVector(inputA, batch_size);

  std::vector<seal::Plaintext> plainB =
      context.encodeVector(inputB, batch_size);

  std::vector<seal::Ciphertext> cipher_dot =
      kernel_executor.dotPlainBatchAxis(ciphersA, plainB, 4, 3, 2);

  std::vector<seal::Plaintext> decrypted = context.decryptVector(cipher_dot);
  std::vector<uint64_t> output = context.decodeVector(decrypted, batch_size);

  checkEqual(output, exp_out);
}

TEST(seal_bfv_kernel_executor, matMulVal10x9x8) {
  int dim1 = 10;
  int dim2 = 9;
  int dim3 = 8;
  SealBFVContext context(8192, std::vector<int>(3, 50), true, true);
  SealBFVKernelExecutor kernel_executor(context);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;

  std::vector<std::vector<int>> my_mat_a(dim1, std::vector<int>(dim2));
  std::vector<std::vector<int>> my_mat_b(dim2, std::vector<int>(dim3));
  std::vector<std::vector<int>> my_trans_b(dim3, std::vector<int>(dim2));

  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, 10);

  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++) my_mat_a[i][j] = distrib(gen);
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_mat_b[i][j] = distrib(gen);
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_trans_b[j][i] = my_mat_b[i][j];

  auto vec_a = generateVector<std::uint64_t>(slot_count, row_size);
  auto vec_b = generateVector<std::uint64_t>(slot_count, row_size);

  // 2d vector for each row/col in Matrix A and trans_matrix B
  std::vector<std::vector<uint64_t>> vec_container_a(dim1, vec_a);
  std::vector<std::vector<uint64_t>> vec_container_b(dim3, vec_b);

  // Populate Vectors with ULL vectors with Matrix A & B's Data
  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++)
      vec_container_a[i][j] = static_cast<uint64_t>(my_mat_a[i][j]);
  for (size_t i = 0; i < dim3; i++)
    for (size_t j = 0; j < dim2; j++)
      vec_container_b[i][j] = static_cast<uint64_t>(my_trans_b[i][j]);

  // Vectors of plaintexts and ciphertexts
  // 1 for each row of Matrix A and of Trans_Matrix B
  std::vector<seal::Plaintext> vec_pt_a(dim1), vec_pt_b(dim3);
  std::vector<seal::Ciphertext> vec_ct_a(dim1), vec_ct_b(dim3);

  // Ciphertext result for output on server
  std::vector<std::vector<seal::Ciphertext>> vec_ct_res(
      vec_ct_a.size(), std::vector<seal::Ciphertext>(vec_ct_b));

  // std::cout << std::endl << "Encoding..." << std::endl;
  for (size_t i = 0; i < dim1; i++)
    context.batch_encoder().encode(vec_container_a[i], vec_pt_a[i]);
  for (size_t i = 0; i < dim3; i++)
    context.batch_encoder().encode(vec_container_b[i], vec_pt_b[i]);

  // std::cout << std::endl << "Encrypting..." << std::endl;
  for (size_t i = 0; i < dim1; i++)
    context.encryptor().encrypt(vec_pt_a[i], vec_ct_a[i]);
  for (size_t i = 0; i < dim3; i++)
    context.encryptor().encrypt(vec_pt_b[i], vec_ct_b[i]);

  // Matrix for holding the "many_sum" of the rotations (can be used by
  // "client") to build the result matrix
  std::vector<std::vector<seal::Ciphertext>> sum(
      dim1, std::vector<seal::Ciphertext>(dim3));

  sum = kernel_executor.matMulVal(vec_ct_a, vec_ct_b, dim1, dim2, dim3);

  std::vector<std::vector<seal::Plaintext>> vec_pt_res(
      dim1, std::vector<seal::Plaintext>(dim3));
  std::vector<std::vector<int64_t>> ret_container(dim1,
                                                  std::vector<int64_t>(dim3));
  std::vector<std::vector<int>> ret_mat(dim1, std::vector<int>(dim3));
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      context.decryptor().decrypt(sum[i][j], vec_pt_res[i][j]);
    }
  }

  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      context.batch_encoder().decode(vec_pt_res[i][j], ret_container[i]);
      ret_mat[i][j] = static_cast<int>(ret_container[i][0]);
    }
  }

  std::vector<std::vector<int>> exp_out(dim1, std::vector<int>(dim3));

  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        exp_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }
  checkEqual(ret_mat, exp_out);
}

TEST(seal_bfv_kernel_executor, matMulRow10x9x8) {
  int dim1 = 10;
  int dim2 = 9;
  int dim3 = 8;
  SealBFVContext context(8192, std::vector<int>(3, 50), true, true);
  SealBFVKernelExecutor kernel_executor(context);

  std::vector<std::vector<int>> my_mat_a(dim1, std::vector<int>(dim2));
  std::vector<std::vector<int>> my_mat_b(dim2, std::vector<int>(dim3));
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> distrib(0, 10);

  for (size_t i = 0; i < dim1; i++)
    for (size_t j = 0; j < dim2; j++) my_mat_a[i][j] = distrib(gen);
  for (size_t i = 0; i < dim2; i++)
    for (size_t j = 0; j < dim3; j++) my_mat_b[i][j] = distrib(gen);

  size_t slot_count = context.batch_encoder().slot_count();
  size_t row_size = slot_count / 2;

  auto vec_a = generateVector<std::uint64_t>(slot_count, row_size);
  auto vec_b = generateVector<std::uint64_t>(slot_count, row_size);

  // Spacing is based on the number of Rows in Matrix B (or Columns in A)
  size_t spacers = row_size / dim2;

  // Populate Vectors with ULL vectors with Matrix A & B's Data
  std::vector<std::vector<uint64_t>> vec_container_a;
  for (size_t i = 0; i < dim1; i += 2) {
    for (size_t j = 0; j < dim2; j++) {
      for (size_t k = 0; k < dim3; k++) {
        vec_a[spacers * j + k] = static_cast<uint64_t>(my_mat_a[i][j]);
        if (i + 1 < dim1)
          vec_a[row_size + (spacers * j + k)] =
              static_cast<uint64_t>(my_mat_a[i + 1][j]);
        if (i == 0) {
          vec_b[spacers * j + k] = static_cast<uint64_t>(my_mat_b[j][k]);
          vec_b[row_size + (spacers * j + k)] =
              static_cast<uint64_t>(my_mat_b[j][k]);
        }
      }
    }
    vec_container_a.push_back(vec_a);
  }

  // Plaintexts and Ciphertexts for input
  seal::Plaintext pt_b;
  std::vector<seal::Plaintext> vec_pt_a(vec_container_a.size());
  seal::Ciphertext ct_b;
  std::vector<seal::Ciphertext> vec_ct_a(vec_container_a.size());

  // Ciphertext result for output on server
  std::vector<seal::Ciphertext> vec_ct_res(vec_ct_a.size());

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

  // # of Columns in A and # of Rows in B information is lost in Ciphertext
  // Will need this information later for determining how many rotations to do
  // size_t mat_a_columns = dim2;

  // Vector of Ciphertexts containing A @ B
  // Each Ciphertext contains the dot prod of two Rows in Matrix A, with every
  // column in Matrix B
  std::vector<seal::Ciphertext> sum(vec_ct_a.size());

  sum = kernel_executor.matMulRow(vec_ct_a, ct_b, dim1, dim2, dim3);

  std::vector<std::vector<int>> ret_mat(dim1, std::vector<int>(dim3));
  std::vector<seal::Plaintext> vec_pt_res(vec_container_a.size());
  std::vector<std::vector<uint64_t>> vec_container_res;
  std::vector<uint64_t> vec_result(slot_count, 0ULL);

  for (size_t i = 0; i < sum.size(); i++)
    context.decryptor().decrypt(sum[i], vec_pt_res[i]);

  for (size_t i = 0; i < sum.size(); i += 2) {
    context.batch_encoder().decode(vec_pt_res[i], vec_result);
    vec_container_res.push_back(vec_result);
    if (i + 1 < sum.size()) {
      context.batch_encoder().decode(vec_pt_res[i + 1], vec_result);
      vec_container_res.push_back(vec_result);
    }
  }

  for (size_t i = 0; i < dim1; i += 2) {
    for (size_t j = 0; j < dim3; j++) {
      ret_mat[i][j] = static_cast<int>(vec_container_res[i / 2][j]);
      if (i + 1 < dim1)
        ret_mat[i + 1][j] =
            static_cast<int>(vec_container_res[i / 2][j + row_size]);
    }
  }

  std::vector<std::vector<int>> exp_out(dim1, std::vector<int>(dim3));

  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      for (size_t k = 0; k < dim2; k++) {
        exp_out[i][j] += my_mat_a[i][k] * my_mat_b[k][j];
      }
    }
  }

  checkEqual(ret_mat, exp_out);
}

}  // namespace heseal
}  // namespace he
}  // namespace intel
