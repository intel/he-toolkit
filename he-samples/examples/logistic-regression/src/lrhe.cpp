// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "include/lrhe.hpp"

#include <chrono>

#include "include/data_loader.hpp"
#include "include/logger.hpp"
#include "include/timer.hpp"

namespace lrhe {
LogisticRegressionHE::LogisticRegressionHE(
    const kernel::LRHEKernel& lrheKernel) {
  init(lrheKernel);
}

void LogisticRegressionHE::init(const kernel::LRHEKernel& lrheKernel) {
  m_kernel = std::make_unique<kernel::LRHEKernel>(lrheKernel);
  m_isTrained = false;
  m_slot_count = m_kernel->slot_count();
}

void LogisticRegressionHE::load_weight(const std::vector<double>& weights,
                                       const double bias) {
  if (m_isTrained) LOG<Info>("  Overwriting weights/bias");

  m_n_weights = weights.size();
  m_weights = weights;
  m_bias = bias;

  LOG<Info>("Encode/encrypt weights and bias");
  m_ct_weights = encodeEncryptWeights(weights);
  m_ct_bias = encodeEncryptBias(bias);
  LOG<Info>("Encode/encrypt weights and bias", "complete");

  m_isTrained = true;
}

std::vector<double> LogisticRegressionHE::inference(
    const std::vector<std::vector<double>>& inputData, bool clipResult) {
  if (!m_isTrained)
    throw std::runtime_error("Logistic Regression model not trained");

  if (inputData.size() < 1) throw std::invalid_argument("InputData is empty");

  if (inputData[0].size() != m_n_weights)
    throw std::invalid_argument("InputData feature size mismatch");

  size_t n_samples = inputData.size();
  LOG<Info>("HE Logistic Regression");

  // Calculate number of batches
  size_t total_batch =
      n_samples / m_slot_count + (n_samples % m_slot_count == 0 ? 0 : 1);
  size_t last_batch_size =
      n_samples % m_slot_count == 0 ? m_slot_count : n_samples % m_slot_count;
  LOG<Info>("  # of batches:", total_batch, " Batch size:", m_slot_count);

  LOG<Info>("  Transpose data");
  std::vector<std::vector<std::vector<double>>> batched_data_T(total_batch);

#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < total_batch; ++i) {
    size_t batchsize = i < total_batch - 1 ? m_slot_count : last_batch_size;
    auto first = inputData.begin() + i * m_slot_count;
    batched_data_T[i] =
        std::vector<std::vector<double>>(first, first + batchsize);
    batched_data_T[i] = transpose(batched_data_T[i]);
  }
  LOG<Info>("  - Transpose data complete");

  // ============================
  // Encode/encrypt inputs
  // ============================
  LOG<Info>("  Encode/encrypt data");
  auto t_started = intel::timer::now();

  std::vector<std::vector<seal::Ciphertext>> ct_inputs =
      encodeEncryptData(batched_data_T);

  LOG<Info>("  - Encode/encrypt data complete!",
            "Elapsed(s):", intel::timer::delta(t_started));

  // ================================
  // Logistic Regression HE inference
  // ================================
  std::vector<seal::Ciphertext> ct_lrhe_inference(total_batch);
  LOG<Info>("  LR HE:", total_batch, "batch(es)");
  t_started = intel::timer::now();
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < total_batch; ++i)
    ct_lrhe_inference[i] = m_kernel->evaluateLogisticRegressionTransposed(
        m_ct_weights, ct_inputs[i], m_ct_bias);
  LOG<Info>("  - LR HE complete!",
            "Elapsed(s):", intel::timer::delta(t_started));

  // ========================
  // Decrypt/decode HE result
  // ========================
  LOG<Info>("  Decrypt/decoding LRHE result");
  t_started = intel::timer::now();
  std::vector<double> retval =
      decryptDecodeResult(ct_lrhe_inference, n_samples);
  LOG<Info>("  - Decrypt/decode complete!",
            "Elapsed(s):", intel::timer::delta(t_started));

  // clip result to 0 or 1
  if (clipResult)
    std::transform(
        retval.begin(), retval.end(), retval.begin(),
        [](const double& val) { return static_cast<int>(0.5 + val); });

  return std::vector<double>(retval.begin(), retval.begin() + n_samples);
}

seal::Ciphertext LogisticRegressionHE::encodeEncryptBias(const double bias) {
  return m_kernel->encrypt(m_kernel->encode(
      gsl::span(std::vector<double>(m_slot_count, bias).data(), m_slot_count)));
}

std::vector<double> LogisticRegressionHE::decryptDecodeResult(
    const std::vector<seal::Ciphertext> ct_result_batches, size_t n_samples) {
  size_t n_batches = ct_result_batches.size();
  std::vector<double> ret(n_batches * m_slot_count);

#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < n_batches; ++i) {
    seal::Plaintext pt_buf;
    m_kernel->decryptor().decrypt(ct_result_batches[i], pt_buf);
    std::vector<double> buf;
    m_kernel->encoder().decode(pt_buf, buf);
    std::copy_n(buf.begin(), m_slot_count, &ret[i * m_slot_count]);
  }

  return std::vector<double>(ret.begin(), ret.begin() + n_samples);
}

std::vector<std::vector<seal::Ciphertext>>
LogisticRegressionHE::encodeEncryptData(
    const std::vector<std::vector<std::vector<double>>>& data_T) {
  size_t n_batches = data_T.size();
  size_t n_features = data_T[0].size();

  std::vector<std::vector<seal::Ciphertext>> ct_ret(
      n_batches, std::vector<seal::Ciphertext>(n_features));

#pragma omp parallel for collapse(2) \
    num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < n_batches; ++i)
    for (size_t j = 0; j < n_features; ++j)
      ct_ret[i][j] = m_kernel->encrypt(m_kernel->encode(
          gsl::span(data_T[i][j].data(), data_T[i][j].size())));

  return ct_ret;
}

std::vector<seal::Ciphertext> LogisticRegressionHE::encodeEncryptWeights(
    const std::vector<double>& weights) {
  size_t n_features = weights.size();
  std::vector<seal::Ciphertext> ct_ret(n_features);

#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < n_features; ++i)
    ct_ret[i] = m_kernel->encrypt(m_kernel->encode(gsl::span(
        std::vector<double>(m_slot_count, weights[i]).data(), m_slot_count)));

  return ct_ret;
}
}  // namespace lrhe
