// Copyright (C) 2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LRHE_HPP_
#define HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LRHE_HPP_

#pragma once

#include <seal/seal.h>

#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "kernels/lrhe_kernel.hpp"

namespace lrhe {
class LRHE {
 public:
  LRHE() {}
  LRHE(const kernel::LRHEKernel& lrheKernel, const bool encrypt_data = true,
       const bool encrypt_model = true, const bool linear_regression = false,
       const size_t batch_size = 0);

  ~LRHE() {}

  // Initialize LRHE with LRHEKernel
  // @param lrheKernel backend kernel class handling HE operations
  void init(const kernel::LRHEKernel& lrheKernel);

  // Load weight and bias, then encode/encrypt for LRHE inference
  // @param weights weight vector of LR model
  // @param bias bias of LR model
  void load_weight(const std::vector<double>& weights, const double bias);

  std::vector<double> get_weights() { return m_weights; }
  double get_bias() { return m_bias; }

  // Runs LR inference in SEAL CKKS HE
  std::vector<double> inference(
      const std::vector<std::vector<double>>& inputData,
      bool clipResult = true);

 protected:
  bool m_linear_regression = false;

 private:
  bool m_encrypt_data = true;
  bool m_encrypt_model = true;

  std::unique_ptr<kernel::LRHEKernel> m_kernel;
  bool m_isTrained;

  size_t m_slot_count;
  size_t m_batch_size;
  std::vector<double> m_weights;
  double m_bias;
  size_t m_n_weights;
  std::vector<seal::Ciphertext> m_ct_weights;
  seal::Ciphertext m_ct_bias;
  std::vector<seal::Plaintext> m_pt_weights;
  seal::Plaintext m_pt_bias;

  seal::Ciphertext encodeEncryptBias(const double bias);
  seal::Plaintext encodeBias(const double bias);
  std::vector<double> decryptDecodeResult(
      const std::vector<seal::Ciphertext> ct_result_batches, size_t n_samples);
  std::vector<std::vector<seal::Ciphertext>> encodeEncryptData(
      const std::vector<std::vector<std::vector<double>>>& data_T);
  std::vector<std::vector<seal::Plaintext>> encodeData(
      const std::vector<std::vector<std::vector<double>>>& data_T);
  std::vector<seal::Ciphertext> encodeEncryptWeights(
      const std::vector<double>& weights);
  std::vector<seal::Plaintext> encodeWeights(
      const std::vector<double>& weights);
};

class LogisticRegressionHE : public LRHE {
 public:
  LogisticRegressionHE() {}
  LogisticRegressionHE(const kernel::LRHEKernel& lrheKernel,
                       const bool encrypt_data = true,
                       const bool encrypt_model = true,
                       const size_t batch_size = 0)
      : LRHE(lrheKernel, encrypt_data, encrypt_model, false, batch_size) {}
};

class LinearRegressionHE : public LRHE {
 public:
  LinearRegressionHE() { m_linear_regression = true; }
  LinearRegressionHE(const kernel::LRHEKernel& lrheKernel,
                     const bool encrypt_data = true,
                     const bool encrypt_model = true,
                     const size_t batch_size = 0)
      : LRHE(lrheKernel, encrypt_data, encrypt_model, true, batch_size) {}
};
}  // namespace lrhe
#endif  // HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LRHE_HPP_
