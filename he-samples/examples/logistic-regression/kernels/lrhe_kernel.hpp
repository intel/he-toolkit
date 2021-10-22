// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_KERNELS_LRHE_KERNEL_HPP_
#define HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_KERNELS_LRHE_KERNEL_HPP_

#pragma once

#include <seal/seal.h>

#include <gsl/span>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "omp_utils.h"
namespace kernel {
class LRHEKernel {
 public:
  LRHEKernel(size_t poly_modulus_degree, std::vector<int> coeff_modulus,
             double scale, bool generate_relin_keys = true,
             bool generate_galois_keys = true,
             seal::sec_level_type sec_level = seal::sec_level_type::none)
      : m_poly_modulus_degree(poly_modulus_degree),
        m_scale(scale),
        m_sec_level(sec_level) {
    initContext(poly_modulus_degree, coeff_modulus, scale, generate_relin_keys,
                generate_galois_keys);
  }

  void initContext(size_t poly_modulus_degree, std::vector<int> coeff_modulus,
                   double scale, bool generate_relin_keys = true,
                   bool generate_galois_keys = true);

  // Encodes vector to a single plaintext
  // @param v input vector. size should be smaller or equal to slot_count
  // @return pt_ret encoded result
  seal::Plaintext encode(const gsl::span<const double>& v);
  seal::Ciphertext encrypt(const seal::Plaintext& v);
  seal::Plaintext decryptVector(const seal::Ciphertext& v);
  std::vector<double> decodeVector(const seal::Plaintext& v);

  seal::Ciphertext encodeEncryptBias(const double bias);
  std::vector<std::vector<seal::Ciphertext>> encodeEncryptData(
      const std::vector<std::vector<std::vector<double>>>& data_T);
  std::vector<seal::Ciphertext> encodeEncryptWeights(
      const std::vector<double>& weights);

  std::vector<double> decryptDecodeResult(
      const std::vector<seal::Ciphertext> ct_result_batches, size_t n_samples);

  seal::Ciphertext accumulate_internal(const seal::Ciphertext& A);

  seal::Ciphertext accumulate_chunks(const std::vector<seal::Ciphertext>& A);

  seal::Ciphertext mean_vector(const std::vector<seal::Ciphertext>& A,
                               const size_t count);

  virtual seal::Ciphertext vecMatProduct(
      const std::vector<seal::Ciphertext>& A_T_extended,
      const std::vector<seal::Ciphertext>& B);
  virtual seal::Ciphertext vecMatProduct(
      const std::vector<seal::Ciphertext>& A_T_extended,
      const std::vector<seal::Plaintext>& B);
  virtual seal::Ciphertext vecMatProduct(
      const std::vector<seal::Plaintext>& A_T_extended,
      const std::vector<seal::Ciphertext>& B);

  // Performs polynomial function evaluation using conventional method
  // @param inputs Ciphertext of vector
  // @param coefficients coefficients of a polynomial function, which the order
  // is {a(0), a(1), a(2), ..., a(n-1)} where f(x)=a(0)+a(1)x + a(2)x^2 + ... +
  // a(n-1)x^(n-1)
  // @param is_minus Set to true to calculate f(-x)
  // @return retval elementwise polynomial of all slots in the input ciphertext
  seal::Ciphertext evaluatePolynomialVector(
      const seal::Ciphertext& inputs,
      const gsl::span<const double>& coefficients, bool is_minus = false);

  // Performs polynomial function evaluation using Horner method
  // @param inputs Ciphertext of vector
  // @param coefficients coefficients of a polynomial function, which the order
  // is {a(0), a(1), a(2), ..., a(n-1)} where f(x)=a(0)+a(1)x + a(2)x^2 + ... +
  // a(n-1)x^(n-1)
  // @param is_minus Set to true to calculate f(-x)
  // @return retval elementwise polynomial of all slots in the input ciphertext
  seal::Ciphertext evaluatePolynomialVectorHorner(
      const seal::Ciphertext& inputs,
      const gsl::span<const double>& coefficients, bool is_minus = false);

  // Performs polynomial sigmoid evaluation on a given Ciphertext input
  // @param inputs Ciphertext of vector
  // @param is_minus Set to true to get sigmoid(-x)
  // @return retval elementwise polynomial sigmoid of all slots in the input
  // ciphertext
  template <unsigned int degree = 3>
  seal::Ciphertext sigmoid_vector(const seal::Ciphertext& inputs,
                                  bool is_minus = false);

  // Performs linear regression with transposed inputs for faster inference
  // @param weights_T_extended Ciphertext of transpose of weight vector which is
  // extended column-wise to match data size
  // @param inputs_T Ciphertext of transpose of input where each row and column
  // are features and inputs, respectively
  // @param bias_extended Ciphertext of bias which is extended to be a vector to
  // match data size
  // @return retval linear regression HE inference result
  seal::Ciphertext evaluateLinearRegressionTransposed(
      std::vector<seal::Ciphertext> weights_T_extended,
      std::vector<seal::Ciphertext>& inputs_T, seal::Ciphertext bias_extended);
  seal::Ciphertext evaluateLinearRegressionTransposed(
      std::vector<seal::Ciphertext> weights_T_extended,
      std::vector<seal::Plaintext>& inputs_T, seal::Ciphertext bias_extended);
  seal::Ciphertext evaluateLinearRegressionTransposed(
      std::vector<seal::Plaintext> weights_T_extended,
      std::vector<seal::Ciphertext>& inputs_T, seal::Plaintext bias_extended);

  // Performs logistic regression with transposed inputs for faster inference
  // @param weights_T_extended Ciphertext of transpose of weight vector which is
  // extended column-wise to match data size
  // @param inputs_T Ciphertext of transpose of input where each row and column
  // are features and inputs, respectively
  // @param bias_extended Ciphertext of bias which is extended to be a vector to
  // match data size
  // @param sigmoid_degree Degree of polynomial representation of sigmoid
  // function, options = 3,5,7
  // @return retval logistic regression HE inference result
  seal::Ciphertext evaluateLogisticRegressionTransposed(
      std::vector<seal::Ciphertext> weights_T_extended,
      std::vector<seal::Ciphertext>& inputs_T, seal::Ciphertext bias_extended,
      unsigned int sigmoid_degree = 3);
  seal::Ciphertext evaluateLogisticRegressionTransposed(
      std::vector<seal::Ciphertext> weights_T_extended,
      std::vector<seal::Plaintext>& inputs_T, seal::Ciphertext bias_extended,
      unsigned int sigmoid_degree = 3);
  seal::Ciphertext evaluateLogisticRegressionTransposed(
      std::vector<seal::Plaintext> weights_T_extended,
      std::vector<seal::Ciphertext>& inputs_T, seal::Plaintext bias_extended,
      unsigned int sigmoid_degree = 3);

  //  Modulus switches a and b such that their levels match
  void matchLevel(seal::Ciphertext* a, seal::Ciphertext* b) const;
  void matchLevel(seal::Ciphertext* a, seal::Plaintext* b) const;
  inline void matchLevel(seal::Plaintext* a, seal::Ciphertext* b) const {
    matchLevel(b, a);
  }

  // Returns the level of the ciphertext
  size_t getLevel(const seal::Ciphertext& cipher) const {
    return m_context->get_context_data(cipher.parms_id())->chain_index();
  }

  // Returns the level of the plaintext
  size_t getLevel(const seal::Plaintext& plain) const {
    return m_context->get_context_data(plain.parms_id())->chain_index();
  }

  seal::CKKSEncoder& encoder() { return *m_encoder; }
  seal::Encryptor& encryptor() { return *m_encryptor; }
  seal::Decryptor& decryptor() { return *m_decryptor; }
  seal::Evaluator& evaluator() { return *m_evaluator; }
  const seal::EncryptionParameters& parms() const { return m_parms; }
  const seal::PublicKey& public_key() const { return m_public_key; }
  const seal::SecretKey& secret_key() const { return m_secret_key; }
  const seal::RelinKeys& relin_keys() const { return m_relin_keys; }
  const seal::GaloisKeys& galois_keys() const { return m_galois_keys; }
  std::shared_ptr<seal::SEALContext> context() { return m_context; }

  const size_t slot_count() const { return m_slot_count; }
  int poly_modulus_degree() const { return m_poly_modulus_degree; }
  double scale() const { return m_scale; }

 private:
  static const double sigmoid_coeff_3[];
  static const double sigmoid_coeff_5[];
  static const double sigmoid_coeff_7[];

  std::shared_ptr<seal::KeyGenerator> m_keygen;
  seal::PublicKey m_public_key;
  seal::SecretKey m_secret_key;
  seal::RelinKeys m_relin_keys;
  seal::GaloisKeys m_galois_keys;
  std::shared_ptr<seal::Encryptor> m_encryptor;
  std::shared_ptr<seal::Evaluator> m_evaluator;
  std::shared_ptr<seal::Decryptor> m_decryptor;
  std::shared_ptr<seal::CKKSEncoder> m_encoder;

  std::shared_ptr<seal::SEALContext> m_context;
  int m_poly_modulus_degree;
  double m_scale;
  seal::EncryptionParameters m_parms{seal::scheme_type::ckks};
  size_t m_slot_count;
  seal::sec_level_type m_sec_level;
};

template <>
inline seal::Ciphertext LRHEKernel::sigmoid_vector<3>(
    const seal::Ciphertext& inputs, bool is_minus) {
  return evaluatePolynomialVector(inputs, gsl::span(sigmoid_coeff_3, 4),
                                  is_minus);
}

template <>
inline seal::Ciphertext LRHEKernel::sigmoid_vector<5>(
    const seal::Ciphertext& inputs, bool is_minus) {
  return evaluatePolynomialVectorHorner(inputs, gsl::span(sigmoid_coeff_5, 6),
                                        is_minus);
}

template <>
inline seal::Ciphertext LRHEKernel::sigmoid_vector<7>(
    const seal::Ciphertext& inputs, bool is_minus) {
  return evaluatePolynomialVectorHorner(inputs, gsl::span(sigmoid_coeff_7, 8),
                                        is_minus);
}
}  // namespace kernel
#endif  // HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_KERNELS_LRHE_KERNEL_HPP_
