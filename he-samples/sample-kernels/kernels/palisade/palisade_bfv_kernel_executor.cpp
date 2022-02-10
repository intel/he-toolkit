// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "kernels/palisade/palisade_bfv_kernel_executor.h"

#include <omp.h>

#include <stdexcept>
#include <utility>

#include "kernels/palisade/palisade_omp_utils.h"

namespace intel {
namespace he {
namespace palisade {

PalisadeBFVKernelExecutor::PalisadeBFVKernelExecutor(
    lbcrypto::CryptoContext<lbcrypto::DCRTPoly>& cc,
    lbcrypto::LPPublicKey<lbcrypto::DCRTPoly>& public_key) {
  if (!cc) throw std::invalid_argument("cc cannot be null.");
  if (!public_key) throw std::invalid_argument("public_key cannot be null.");
  m_context = cc;
  m_public_key = public_key;
}

std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>
PalisadeBFVKernelExecutor::dotPlainBatchAxis(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& arg1,
    const std::vector<lbcrypto::Plaintext>& arg2, size_t dim1, size_t dim2,
    size_t dim3) {
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> out(dim1 * dim3);

  int omp_remaining_threads = OMPUtilitiesP::MaxThreads;
  // WARNING: Parallelizing outer loop causes errors in Palisade for some
  // reason. Exception thrown about *= not implemented: possible parallelism
  // unfriendly code in Palisade. This does not happen on CKKS.
  /*#pragma omp parallel for collapse(2) num_threads(\
      OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, dim1 * dim3))//*/
  for (size_t out_ind1 = 0; out_ind1 < dim1; ++out_ind1) {
#pragma omp parallel for num_threads( \
    OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, dim3))
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
PalisadeBFVKernelExecutor::dotCipherBatchAxis(
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
          out[out_idx] = m_context->EvalMult(arg1[arg1_idx], arg2[arg2_idx]);
          continue;
        }
        out[out_idx] += m_context->EvalMult(arg1[arg1_idx], arg2[arg2_idx]);
      }
    }
  }
  return out;
}

std::vector<std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>>
PalisadeBFVKernelExecutor::matMulEIP(
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
PalisadeBFVKernelExecutor::matMulVal(
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
PalisadeBFVKernelExecutor::matMulRow(
    const std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>>& vec_cipher_a,
    const lbcrypto::Ciphertext<lbcrypto::DCRTPoly>& cipher_b, size_t dim1,
    size_t dim2, size_t dim3, int64_t slots) {
  std::vector<lbcrypto::Ciphertext<lbcrypto::DCRTPoly>> sum(dim1);

  int64_t spacers = slots / dim2;

  lbcrypto::Plaintext plain_zero =
      m_context->MakePackedPlaintext(std::vector<int64_t>{0});
  lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_zero =
      m_context->Encrypt(m_public_key, plain_zero);
  plain_zero.reset();

  int inner_threads = OMPUtilitiesP::MaxThreads / vec_cipher_a.size() - 1;
  if (inner_threads <= 0)
    inner_threads = 1;
  else if (inner_threads > vec_cipher_a.size())
    inner_threads = vec_cipher_a.size();
  int omp_remaining_threads = OMPUtilitiesP::MaxThreads;
#pragma omp parallel for num_threads(OMPUtilitiesP::assignOMPThreads( \
    omp_remaining_threads, vec_cipher_a.size()))
  for (size_t i = 0; i < vec_cipher_a.size(); i++) {
    lbcrypto::Ciphertext<lbcrypto::DCRTPoly> cipher_res_tmp =
        m_context->EvalMult(vec_cipher_a[i], cipher_b);
    lbcrypto::Ciphertext<lbcrypto::DCRTPoly> tmp_sum = cipher_zero;
#pragma omp declare reduction(+: \
                            lbcrypto::Ciphertext<lbcrypto::DCRTPoly>: \
                            omp_out += omp_in) \
                            initializer(omp_priv = omp_orig)
#pragma omp parallel for reduction(+: tmp_sum) num_threads(\
    OMPUtilitiesP::assignOMPThreads(omp_remaining_threads, inner_threads))
    for (int32_t k = 1; k < dim2; k++) {
      tmp_sum += m_context->EvalAtIndex(cipher_res_tmp, k * spacers);
    }
    sum[i] = tmp_sum + cipher_res_tmp;
  }
  return sum;
}

}  // namespace palisade
}  // namespace he
}  // namespace intel
