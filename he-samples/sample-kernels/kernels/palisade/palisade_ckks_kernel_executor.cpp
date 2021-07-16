// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "kernels/palisade/palisade_ckks_kernel_executor.h"

#include <stdexcept>
#include <utility>

#include "palisade_omp_utils.h"

namespace intel {
namespace he {
namespace palisade {

const double PalisadeCKKSKernelExecutor::sigmoid_coeff_3[] = {0.5, 0.15012, 0.0,
                                                              -0.001593008};
const double PalisadeCKKSKernelExecutor::sigmoid_coeff_5[] = {
    0.5, 0.19131, 0.0, -0.0045963, 0.0, 0.000041233};
const double PalisadeCKKSKernelExecutor::sigmoid_coeff_7[] = {
    0.5, 0.21687, 0.0, -0.008191543, 0.0, 0.000165833, 0.0, 0.000001196};

PalisadeCKKSKernelExecutor::PalisadeCKKSKernelExecutor(
    lbcrypto::CryptoContext<lbcrypto::DCRTPoly>& cc,
    lbcrypto::LPPublicKey<lbcrypto::DCRTPoly>& public_key,
    lbcrypto::RescalingTechnique rescaling_technique) {
  if (!cc) throw std::invalid_argument("cc cannot be null.");
  if (!public_key) throw std::invalid_argument("public_key cannot be null.");
  m_context = cc;
  m_public_key = public_key;
  m_rescaling_technique = rescaling_technique;
}

lbcrypto::Ciphertext<lbcrypto::DCRTPoly> PalisadeCKKSKernelExecutor::add(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& A,
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& B) {
  B->SetScalingFactor(A->GetScalingFactor());
  return m_context->EvalAdd(A, B);
}

lbcrypto::Ciphertext<lbcrypto::DCRTPoly> PalisadeCKKSKernelExecutor::accumulate(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& V, size_t batch_size) {
  if (batch_size == 0) {
    throw std::runtime_error(
        "PalisadeCKKSKernelExecutor::accumulate requires batch_size > 0");
  }
  return m_context->EvalSum(V, batch_size);
}

lbcrypto::Ciphertext<lbcrypto::DCRTPoly> PalisadeCKKSKernelExecutor::dot(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& A,
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& B, size_t batch_size) {
  if (batch_size == 0) {
    throw std::runtime_error(
        "PalisadeCKKSKernelExecutor::dot requires batch_size > 0");
  }

  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> retval =
      m_context->EvalInnerProduct(A, B, batch_size);
  return m_context->Rescale(retval);
}

std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>
PalisadeCKKSKernelExecutor::matMul(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& A,
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& B_T,
    size_t cols) {
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> retval(A.size() *
                                                               B_T.size());
  int omp_remaining_threads = OMPUtilitiesP::MaxThreads;
#pragma omp parallel for collapse(2) num_threads( \
    OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, retval.size()))
  for (std::size_t A_r = 0; A_r < A.size(); ++A_r)
    for (std::size_t B_T_r = 0; B_T_r < B_T.size(); ++B_T_r) {
      std::size_t i = A_r * cols + B_T_r;
      retval[i++] = dot(A[A_r], B_T[B_T_r], cols);
    }
  return retval;
}

lbcrypto::Ciphertext<lbcrypto::DCRTPoly>
PalisadeCKKSKernelExecutor::evaluatePolynomial(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs,
    const double* coefficients, size_t cnt) {
  if (!coefficients || cnt == 0)
    throw std::invalid_argument("coefficients cannot be null.");
  return evaluatePolynomial(
      inputs, std::vector<double>(coefficients, coefficients + cnt));
}

lbcrypto::Ciphertext<lbcrypto::DCRTPoly>
PalisadeCKKSKernelExecutor::evaluatePolynomial(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& inputs,
    const std::vector<double>& coefficients) {
  return m_context->EvalPoly(inputs, coefficients);
}

lbcrypto::Ciphertext<lbcrypto::DCRTPoly>
PalisadeCKKSKernelExecutor::evaluateLinearRegression(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& w,
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& inputs,
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& bias,
    size_t weights_count) {
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> tmp;
  tmp.emplace_back(w);
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> retval =
      m_context->EvalMerge(matMul(tmp, inputs, weights_count));
  return m_context->EvalAdd(retval, bias);
}

lbcrypto::Ciphertext<lbcrypto::DCRTPoly>
PalisadeCKKSKernelExecutor::evaluateLogisticRegression(
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& w,
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& inputs,
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& bias, size_t weights_count,
    unsigned int sigmoid_degree) {
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> retval =
      evaluateLinearRegression(w, inputs, bias, weights_count);
  switch (sigmoid_degree) {
    case 5:
      retval = sigmoid<5>(retval);
      break;
    case 7:
      retval = sigmoid<7>(retval);
      break;
    default:
      retval = sigmoid<3>(retval);
      break;
  }
  return retval;
}

std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>>
PalisadeCKKSKernelExecutor::matMulEIP(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_a,
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_b,
    size_t dim1, size_t dim2, size_t dim3, size_t batch_size) {
  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> out(
      dim1, std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>(dim3));

#pragma omp parallel for collapse(2)
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      out[i][j] =
          m_context->EvalInnerProduct(cipher_a[i], cipher_b[j], batch_size);
    }
  }
  return out;
}

std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>>
PalisadeCKKSKernelExecutor::matMulVal(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_a,
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& cipher_b,
    size_t dim1, size_t dim2, size_t dim3) {
  std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>> sum(
      dim1, std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>(dim3));

  int omp_remaining_threads = OMPUtilitiesP::MaxThreads;
#pragma omp parallel for collapse(2) num_threads( \
    OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, dim1* dim3))
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_res_tmp =
          m_context->EvalMult(cipher_a[i], cipher_b[j]);
      sum[i][j] = m_context->EvalSum(cipher_res_tmp, dim2);
    }
  }
  return sum;
}

std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>
PalisadeCKKSKernelExecutor::matMulRow(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& vec_cipher_a,
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& cipher_b, size_t dim1,
    size_t dim2, size_t dim3, int64_t slots) {
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> sum(dim1);

  int64_t spacers = slots / dim2;

  lbcrypto::Plaintext plain_zero =
      m_context->MakeCKKSPackedPlaintext(std::vector<double>{0});
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_zero =
      m_context->Encrypt(m_public_key, plain_zero);
  plain_zero.reset();

  int inner_threads = OMPUtilitiesP::MaxThreads / vec_cipher_a.size() - 1;
  inner_threads =
      std::clamp(inner_threads, 1, static_cast<int>(vec_cipher_a.size()));
  int omp_remaining_threads = OMPUtilitiesP::MaxThreads;
#pragma omp parallel for num_threads(OMPUtilitiesP::assignOMPThreads( \
    omp_remaining_threads, vec_cipher_a.size()))
  for (size_t i = 0; i < vec_cipher_a.size(); i++) {
    lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_res_tmp =
        m_context->EvalMult(vec_cipher_a[i], cipher_b);
    auto cPrecomp = m_context->EvalFastRotationPrecompute(cipher_res_tmp);
    lbcrypto::Ciphertext<lbcrypto::DCRTPoly> tmp_sum = cipher_zero;

    // Need Depth of the two ciphertexts to be the same for the coming
    // operation. However, Rescaling when using BV would put the ciphertext in a
    // state where the digits aren't smaller, and noise would corrupt the
    // result. Instead of Rescaling and increasing the relinWindow, we simply
    // set the depth accordingly and leave relinWindow = 0 for max performance
    // while keeping accuracy.
    tmp_sum->SetDepth(cipher_res_tmp->GetDepth());
#pragma omp declare reduction(+: \
                            lbcrypto::Ciphertext<lbcrypto::DCRTPoly>: \
                            omp_out += omp_in) \
                            initializer(omp_priv = omp_orig)
#pragma omp parallel for reduction(+: tmp_sum) num_threads(\
    OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, inner_threads))
    for (int32_t k = 1; k < dim2; k++) {
      tmp_sum += m_context->EvalFastRotation(cipher_res_tmp, k * spacers,
                                             slots * 4, cPrecomp);
    }
    sum[i] = tmp_sum + cipher_res_tmp;
  }
  return sum;
}

std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>
PalisadeCKKSKernelExecutor::dotPlainBatchAxis(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& arg1,
    const std::vector<lbcrypto::Plaintext>& arg2, size_t dim1, size_t dim2,
    size_t dim3) {
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> out(dim1 * dim3);

  int omp_remaining_threads = OMPUtilitiesP::MaxThreads;
#pragma omp parallel for collapse(2) num_threads( \
    OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, dim1* dim3))
  for (size_t out_ind1 = 0; out_ind1 < dim1; ++out_ind1) {
    for (size_t out_ind2 = 0; out_ind2 < dim3; ++out_ind2) {
      size_t out_idx = colMajorIndex(dim1, dim3, out_ind1, out_ind2);
      for (size_t inner_dim = 0; inner_dim < dim2; inner_dim++) {
        size_t arg1_idx = colMajorIndex(dim1, dim2, out_ind1, inner_dim);
        size_t arg2_idx = colMajorIndex(dim2, dim3, inner_dim, out_ind2);
        if (inner_dim == 0) {
          out[out_idx] = m_context->EvalMult(arg1[arg1_idx], arg2[arg2_idx]);
          continue;
        }
        out[out_idx] += m_context->EvalMult(arg1[arg1_idx], arg2[arg2_idx]);
      }
    }
  }
  return out;
}

std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>
PalisadeCKKSKernelExecutor::dotCipherBatchAxis(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& arg1,
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& arg2,
    size_t dim1, size_t dim2, size_t dim3) {
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> out(dim1 * dim3);

  int omp_remaining_threads = OMPUtilitiesP::MaxThreads;
#pragma omp parallel for collapse(2) num_threads( \
    OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, dim1* dim3))
  for (size_t out_ind1 = 0; out_ind1 < dim1; ++out_ind1) {
    for (size_t out_ind2 = 0; out_ind2 < dim3; ++out_ind2) {
      size_t out_idx = colMajorIndex(dim1, dim3, out_ind1, out_ind2);
      for (size_t inner_dim = 0; inner_dim < dim2; inner_dim++) {
        size_t arg1_idx = colMajorIndex(dim1, dim2, out_ind1, inner_dim);
        size_t arg2_idx = colMajorIndex(dim2, dim3, inner_dim, out_ind2);
        if (inner_dim == 0) {
          out[out_idx] =
              m_context->EvalMultNoRelin(arg1[arg1_idx], arg2[arg2_idx]);
          continue;
        }
        out[out_idx] +=
            m_context->EvalMultNoRelin(arg1[arg1_idx], arg2[arg2_idx]);
      }
    }
  }
  for (size_t out_idx = 0; out_idx < dim1 * dim3; ++out_idx) {
    out[out_idx] = m_context->Relinearize(out[out_idx]);
    out[out_idx] = m_context->Rescale(out[out_idx]);
  }
  return out;
}

}  // namespace palisade
}  // namespace he
}  // namespace intel
