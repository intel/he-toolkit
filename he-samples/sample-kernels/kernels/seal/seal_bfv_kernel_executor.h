// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <seal/seal.h>

#include <memory>
#include <vector>

#include "kernels/seal/seal_bfv_context.h"

namespace intel {
namespace he {
namespace heseal {

class SealBFVKernelExecutor {
 public:
  explicit SealBFVKernelExecutor(
      const seal::EncryptionParameters& params,
      const seal::PublicKey& public_key,
      const seal::RelinKeys& relin_keys = seal::RelinKeys(),
      const seal::GaloisKeys& galois_keys = seal::GaloisKeys());

  SealBFVKernelExecutor(SealBFVContext& seal_bfv_context)
      : SealBFVKernelExecutor(
            seal_bfv_context.parms(), seal_bfv_context.public_key(),
            seal_bfv_context.relin_keys(), seal_bfv_context.galois_keys()) {}

  ~SealBFVKernelExecutor();

  // Performs a ciphertext-plaintext dot product.
  // @param arg1 Ciphertext of shape (dim0 x dim1) in column-major format
  // @param arg2 Plaintext of shape (dim1 x dim2) in column-major format
  // @param dim0 Input shape dimension
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @return A ciphertext matrix of dimension (dim0 x dim2) in row-major format
  std::vector<seal::Ciphertext> dotPlainBatchAxis(
      const std::vector<seal::Ciphertext>& arg1,
      const std::vector<seal::Plaintext>& arg2, size_t dim0, size_t dim1,
      size_t dim2);

  // Performs a ciphertext-cihpertext dot product.
  // @param arg1 Ciphertext of shape (dim0 x dim1) in column-major format
  // @param arg2 Ciphertext of shape (dim1 x dim2) in column-major format
  // @param dim0 Input shape dimension
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @return A ciphertext matrix of dimension (dim0 x dim2) in row-major format
  std::vector<seal::Ciphertext> dotCipherBatchAxis(
      const std::vector<seal::Ciphertext>& arg1,
      const std::vector<seal::Ciphertext>& arg2, size_t dim0, size_t dim1,
      size_t dim2);

  seal::Ciphertext accumulate(const seal::Ciphertext& cipher_input,
                              std::size_t count);

  std::vector<std::vector<seal::Ciphertext>> matMulVal(
      const std::vector<seal::Ciphertext>& A,
      const std::vector<seal::Ciphertext>& B_T, size_t dim1, size_t dim2,
      size_t dim3);

  std::vector<seal::Ciphertext> matMulRow(
      const std::vector<seal::Ciphertext>& A, const seal::Ciphertext& B,
      size_t dim1, size_t dim2, size_t dim3);

  //  Modulus switches a and b such that their levels match
  void matchLevel(seal::Ciphertext* a, seal::Ciphertext* b) const;

  // Returns the level of the ciphertext
  size_t getLevel(const seal::Ciphertext& cipher) const {
    return m_pcontext->get_context_data(cipher.parms_id())->chain_index();
  }

  // Returns the level of the plaintext
  size_t getLevel(const seal::Plaintext& plain) const {
    return m_pcontext->get_context_data(plain.parms_id())->chain_index();
  }

  std::shared_ptr<seal::Evaluator> getEvaluator() const { return m_pevaluator; }

  // Returns index of coordinate [i,j] of [dim1 x dim2] matrix stored in
  // column-major format
  static size_t colMajorIndex(size_t dim1, size_t dim2, size_t i, size_t j) {
    if (i >= dim1) {
      std::stringstream ss;
      ss << i << " too large for dim1 (" << dim1 << ")";
      throw std::runtime_error(ss.str());
    }
    if (j >= dim2) {
      std::stringstream ss;
      ss << j << " too large for dim2 (" << dim2 << ")";
      throw std::runtime_error(ss.str());
    }
    return i + j * dim1;
  }

 private:
  static const double sigmoid_coeff_3[];
  static const double sigmoid_coeff_5[];
  static const double sigmoid_coeff_7[];

  std::shared_ptr<seal::SEALContext> m_pcontext;
  std::shared_ptr<seal::Evaluator> m_pevaluator;
  std::shared_ptr<seal::Encryptor> m_pencryptor;
  std::shared_ptr<seal::BatchEncoder> m_pbatch_encoder;
  seal::EncryptionParameters m_params;
  seal::PublicKey m_public_key;
  seal::RelinKeys m_relin_keys;
  seal::GaloisKeys m_galois_keys;
  double m_scale;
};

}  // namespace heseal
}  // namespace he
}  // namespace intel
