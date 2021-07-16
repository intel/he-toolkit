// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <seal/seal.h>

#include <memory>
#include <utility>
#include <vector>

#include "kernels/seal/seal_ckks_context.h"

namespace intel {
namespace he {
namespace heseal {

class SealCKKSKernelExecutor {
 public:
  explicit SealCKKSKernelExecutor(
      const seal::EncryptionParameters& params, double scale,
      const seal::PublicKey& public_key,
      const seal::RelinKeys& relin_keys = seal::RelinKeys(),
      const seal::GaloisKeys& galois_keys = seal::GaloisKeys());

  SealCKKSKernelExecutor(SealCKKSContext& seal_ckks_context)
      : SealCKKSKernelExecutor(
            seal_ckks_context.parms(), seal_ckks_context.scale(),
            seal_ckks_context.public_key(), seal_ckks_context.relin_keys(),
            seal_ckks_context.galois_keys()) {}

  virtual ~SealCKKSKernelExecutor();

  // Adds two ciphertext vectors element-wise
  std::vector<seal::Ciphertext> add(const std::vector<seal::Ciphertext>& A,
                                    const std::vector<seal::Ciphertext>& B);

  // Sums together all the ciphertexts in v.
  // Assumes each ciphertext stores batch_size scalars
  // @param batch_size Number of scalars stored in each ciphertext
  // @return A ciphertext storing the sum in the first slot
  seal::Ciphertext accumulate(const std::vector<seal::Ciphertext>& v,
                              size_t count);

  // Performs dot product of A and B
  // @param A vector of ciphertexts
  // @param B vector of ciphertext
  // @param batch_size Number of scalars stored in each ciphertext
  // @returns A ciphertext containing the dot product in the first slot
  seal::Ciphertext dot(const std::vector<seal::Ciphertext>& A,
                       const std::vector<seal::Ciphertext>& B,
                       size_t batch_size);

  std::vector<seal::Ciphertext> matMul(
      const std::vector<std::vector<seal::Ciphertext>>& A,
      const std::vector<std::vector<seal::Ciphertext>>& B_T, size_t cols);

  // Performs vector-matrix product of A_T_extended and B
  // @param A_T_extended extended ciphertext of transpose of vector
  // @param B matrix of ciphertext
  // @returns A vector of ciphertext containing the vector-matrix product
  virtual std::vector<seal::Ciphertext> vecMatProduct(
      const std::vector<std::vector<seal::Ciphertext>>& A_T_extended,
      const std::vector<std::vector<seal::Ciphertext>>& B);

  std::vector<seal::Ciphertext> evaluatePolynomial(
      const std::vector<seal::Ciphertext>& inputs,
      const gsl::span<const double>& coefficients);

  std::vector<seal::Ciphertext> evaluatePolynomialVector(
      const std::vector<seal::Ciphertext>& inputs,
      const gsl::span<const double>& coefficients, size_t inputs_count);

  std::vector<seal::Ciphertext> collapse(
      const std::vector<seal::Ciphertext>& ciphers);

  template <unsigned int degree = 3>
  std::vector<seal::Ciphertext> sigmoid(
      const std::vector<seal::Ciphertext>& inputs);

  template <unsigned int degree = 3>
  std::vector<seal::Ciphertext> sigmoid_vector(
      const std::vector<seal::Ciphertext>& inputs, size_t inputs_count);

  std::vector<seal::Ciphertext> evaluateLinearRegression(
      std::vector<seal::Ciphertext>& weights,
      std::vector<std::vector<seal::Ciphertext>>& inputs,
      seal::Ciphertext& bias, size_t weights_count);

  // Performs linear regression with transposed inputs for faster inference
  // @param weights_T_extended Ciphertext of transpose of weight vector which is
  // extended column-wise to match data size
  // @param inputs_T Ciphertext of transpose of input where each row and column
  // are features and inputs, respectively
  // @param bias_extended Ciphertext of bias which is extended to be a vector to
  // match data size
  // @param inputs_count Number of inputs, equals to width of inputs_T
  std::vector<seal::Ciphertext> evaluateLinearRegressionTransposed(
      std::vector<std::vector<seal::Ciphertext>>& weights_T_extended,
      std::vector<std::vector<seal::Ciphertext>>& inputs_T,
      std::vector<seal::Ciphertext>& bias_extended);

  std::vector<seal::Ciphertext> evaluateLogisticRegression(
      std::vector<seal::Ciphertext>& weights,
      std::vector<std::vector<seal::Ciphertext>>& inputs,
      seal::Ciphertext& bias, size_t weights_count,
      unsigned int sigmoid_degree = 3);

  // Performs logistic regression with transposed inputs for faster inference
  // @param weights_T_extended Ciphertext of transpose of weight vector which is
  // extended column-wise to match data size
  // @param inputs_T Ciphertext of transpose of input where each row and column
  // are features and inputs, respectively
  // @param bias_extended Ciphertext of bias which is extended to be a vector to
  // match data size
  // @param inputs_count Number of inputs, equals to width of inputs_T
  // @param sigmoid_degree Degree of polynomial representation of sigmoid
  // function, options = 3,5,7
  std::vector<seal::Ciphertext> evaluateLogisticRegressionTransposed(
      std::vector<std::vector<seal::Ciphertext>>& weights_T_extended,
      std::vector<std::vector<seal::Ciphertext>>& inputs_T,
      std::vector<seal::Ciphertext>& bias_extended, size_t inputs_count,
      unsigned int sigmoid_degree = 3);

  // Performs a ciphertext-plaintext dot product.
  // @param arg1 Ciphertext of shape (dim0 x dim1) in column-major format
  // @param arg2 Plaintext of shape (dim1 x dim2) in column-major format
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @param dim3 Input shape dimension
  // @return A ciphertext matrix of dimension (dim0 x dim2) in column-major
  // format
  std::vector<seal::Ciphertext> dotPlainBatchAxis(
      const std::vector<seal::Ciphertext>& arg1,
      const std::vector<seal::Plaintext>& arg2, size_t dimi1, size_t dim2,
      size_t dim3);

  // Performs a ciphertext-cihpertext dot product.
  // @param arg1 Ciphertext of shape (dim0 x dim1) in column-major format
  // @param arg2 Ciphertext of shape (dim1 x dim2) in column-major format
  // @param dim1 Input shape dimension
  // @param dim2 Input shape dimension
  // @param dim3 Input shape dimension
  // @return A ciphertext matrix of dimension (dim0 x dim2) in column-major
  // format
  std::vector<seal::Ciphertext> dotCipherBatchAxis(
      const std::vector<seal::Ciphertext>& arg1,
      const std::vector<seal::Ciphertext>& arg2, size_t dim1, size_t dimi2,
      size_t dim3);

  //  Modulus switches a and b such that their levels match
  void matchLevel(seal::Ciphertext* a, seal::Ciphertext* b) const;
  void matchLevel(seal::Ciphertext* a, seal::Plaintext* b) const;
  inline void matchLevel(seal::Plaintext* a, seal::Ciphertext* b) const {
    matchLevel(b, a);
  }

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

  seal::Ciphertext accumulate_internal(const seal::Ciphertext& v, size_t count);

  std::shared_ptr<seal::SEALContext> m_pcontext;
  std::shared_ptr<seal::Evaluator> m_pevaluator;
  std::shared_ptr<seal::Encryptor> m_pencryptor;
  std::shared_ptr<seal::CKKSEncoder> m_pencoder;
  seal::EncryptionParameters m_params;
  seal::PublicKey m_public_key;
  seal::RelinKeys m_relin_keys;
  seal::GaloisKeys m_galois_keys;
  double m_scale;

  std::vector<seal::Plaintext> encodeVector(
      const gsl::span<const double>& values, size_t batch_size);
  std::vector<seal::Plaintext> encodeVector(const gsl::span<const double>& v);
  std::vector<seal::Ciphertext> encryptVector(
      const std::vector<seal::Plaintext>& plain);

  inline std::vector<seal::Ciphertext> encryptVector(
      const gsl::span<const double>& v, size_t batch_size) {
    return encryptVector(encodeVector(v, batch_size));
  }

  std::vector<seal::Ciphertext> encryptVector(
      const gsl::span<const double>& v) {
    return encryptVector(encodeVector(v));
  }
};

template <>
inline std::vector<seal::Ciphertext> SealCKKSKernelExecutor::sigmoid<3>(
    const std::vector<seal::Ciphertext>& inputs) {
  return evaluatePolynomial(inputs, gsl::span(sigmoid_coeff_3, 4));
}

template <>
inline std::vector<seal::Ciphertext> SealCKKSKernelExecutor::sigmoid<5>(
    const std::vector<seal::Ciphertext>& inputs) {
  return evaluatePolynomial(inputs, gsl::span(sigmoid_coeff_5, 6));
}

template <>
inline std::vector<seal::Ciphertext> SealCKKSKernelExecutor::sigmoid<7>(
    const std::vector<seal::Ciphertext>& inputs) {
  return evaluatePolynomial(inputs, gsl::span(sigmoid_coeff_7, 8));
}

template <>
inline std::vector<seal::Ciphertext> SealCKKSKernelExecutor::sigmoid_vector<3>(
    const std::vector<seal::Ciphertext>& inputs, size_t inputs_count) {
  return evaluatePolynomialVector(inputs, gsl::span(sigmoid_coeff_3, 4),
                                  inputs_count);
}

template <>
inline std::vector<seal::Ciphertext> SealCKKSKernelExecutor::sigmoid_vector<5>(
    const std::vector<seal::Ciphertext>& inputs, size_t inputs_count) {
  return evaluatePolynomialVector(inputs, gsl::span(sigmoid_coeff_5, 6),
                                  inputs_count);
}

template <>
inline std::vector<seal::Ciphertext> SealCKKSKernelExecutor::sigmoid_vector<7>(
    const std::vector<seal::Ciphertext>& inputs, size_t inputs_count) {
  return evaluatePolynomialVector(inputs, gsl::span(sigmoid_coeff_7, 8),
                                  inputs_count);
}

}  // namespace heseal
}  // namespace he
}  // namespace intel
