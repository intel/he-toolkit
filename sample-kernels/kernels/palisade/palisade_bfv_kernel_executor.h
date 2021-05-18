// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once
#include <palisade.h>

#include <memory>
#include <vector>

namespace intel {
namespace he {
namespace palisade {

class PalisadeBFVKernelExecutor {
 public:
  explicit PalisadeBFVKernelExecutor(
      lbcrypto::CryptoContext<lbcrypto::DCRTPoly>& cc,
      lbcrypto::LPPublicKey<lbcrypto::DCRTPoly>& public_key);

  // Performs a ciphertext-plaintext dot product.
  // @param arg1 Ciphertext of shape (dim1 x dim2) in column-major format
  // @param arg2 Plaintext of shape (dim2 x dim3) in column-major format
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @param dim3 Input shape dimension
  // @return A ciphertext matrix of dimension (dim1 x dim3) in column-major
  // format
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> dotPlainBatchAxis(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& A,
      const std::vector<lbcrypto::Plaintext>& B, size_t dim1, size_t dim2,
      size_t dim3);

  // Performs a ciphertext-ciphertext dot product.
  // @param arg1 Ciphertext of shape (dim1 x dim2) in column-major format
  // @param arg2 Ciphertext of shape (dim2 x dim3) in column-major format
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @param dim3 Input shape dimension
  // @return A ciphertext matrix of dimension (dim1 x dim3) in column-major
  // format
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> dotCipherBatchAxis(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& A,
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& B,
      size_t dim1, size_t dim2, size_t dim3);

  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> matMulEIP(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_a,
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_b,
      size_t dim1, size_t dim2, size_t dim3, size_t batch_size);

  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> matMulVal(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_a,
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_b,
      size_t dim1, size_t dim2, size_t dim3);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> matMulRow(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& vec_cipher_a,
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& cipher_b, size_t dim1,
      size_t dim2, size_t dim3, int64_t slots);

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
  lbcrypto::CryptoContext<lbcrypto::DCRTPoly> m_context;
  lbcrypto::LPPublicKey<lbcrypto::DCRTPoly> m_public_key;
};

}  // namespace palisade
}  // namespace he
}  // namespace intel
