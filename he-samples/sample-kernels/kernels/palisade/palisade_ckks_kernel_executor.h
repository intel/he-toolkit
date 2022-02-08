// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once
#include <palisade.h>

#include <memory>
#include <vector>

namespace intel {
namespace he {
namespace palisade {

class PalisadeCKKSKernelExecutor {
 public:
  explicit PalisadeCKKSKernelExecutor(
      lbcrypto::CryptoContext<lbcrypto::DCRTPoly>& cc,
      lbcrypto::LPPublicKey<lbcrypto::DCRTPoly>& public_key,
      lbcrypto::RescalingTechnique rescaling_technique =
          lbcrypto::RescalingTechnique::EXACTRESCALE);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> add(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& A,
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& B);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> accumulate(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& V, size_t count);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> dot(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& A,
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& B, size_t count);

  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> matMul(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& A,
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& B_T,
      size_t cols);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> evaluatePolynomial(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs,
      const double* coefficients, size_t cnt);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> evaluatePolynomial(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs,
      const std::vector<double>& coefficients);

  template <unsigned int degree = 3>
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> sigmoid(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> evaluateLinearRegression(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& w,
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& inputs,
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& bias,
      size_t weights_count);

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> evaluateLogisticRegression(
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& w,
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& inputs,
      const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& bias,
      size_t weights_count, unsigned int sigmoid_degree = 3);

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

  // Performs a ciphertext-plaintext dot product.
  // @param arg1 Ciphertext of shape (dim0 x dim1) in column-major format
  // @param arg2 Plaintext of shape (dim1 x dim2) in column-major format
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @param dim3 Input shape dimension
  // @return A ciphertext matrix of dimension (dim0 x dim2) in column-major
  // format
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> dotPlainBatchAxis(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& A,
      const std::vector<lbcrypto::Plaintext>& B, size_t dim1, size_t dim2,
      size_t dim3);

  // Performs a ciphertext-cihpertext dot product.
  // @param arg1 Ciphertext of shape (dim0 x dim1) in column-major format
  // @param arg2 Ciphertext of shape (dim1 x dim2) in column-major format
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @param dim3 Input shape dimension
  // @return A ciphertext matrix of dimension (dim0 x dim2) in column-major
  // format
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> dotCipherBatchAxis(
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& A,
      const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& B,
      size_t dim1, size_t dim2, size_t dim3);

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
  lbcrypto::CryptoContext<lbcrypto::DCRTPoly> m_context;
  lbcrypto::LPPublicKey<lbcrypto::DCRTPoly> m_public_key;
  lbcrypto::RescalingTechnique m_rescaling_technique;
};

template <>
inline lbcrypto::Ciphertext<lbcrypto::DCRTPoly>
PalisadeCKKSKernelExecutor::sigmoid<3>(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs) {
  return evaluatePolynomial(inputs, sigmoid_coeff_3, 4);
}

template <>
inline lbcrypto::Ciphertext<lbcrypto::DCRTPoly>
PalisadeCKKSKernelExecutor::sigmoid<5>(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs) {
  return evaluatePolynomial(inputs, sigmoid_coeff_5, 6);
}

template <>
inline lbcrypto::Ciphertext<lbcrypto::DCRTPoly>
PalisadeCKKSKernelExecutor::sigmoid<7>(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs) {
  return evaluatePolynomial(inputs, sigmoid_coeff_7, 8);
}

}  // namespace palisade
}  // namespace he
}  // namespace intel
