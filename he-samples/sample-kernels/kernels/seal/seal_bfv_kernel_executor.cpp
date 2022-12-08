// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "kernels/seal/seal_bfv_kernel_executor.h"

#include <stdexcept>

#include "kernels/seal/seal_ckks_context.h"
#include "kernels/seal/seal_omp_utils.h"

namespace intel {
namespace he {
namespace heseal {

SealBFVKernelExecutor::SealBFVKernelExecutor(
    const seal::EncryptionParameters& params, const seal::PublicKey& public_key,
    const seal::RelinKeys& relin_keys, const seal::GaloisKeys& galois_keys) {
  if (params.scheme() != seal::scheme_type::bfv)
    throw std::invalid_argument("Only BFV scheme supported.");
  m_public_key = public_key;
  m_relin_keys = relin_keys;
  m_galois_keys = galois_keys;
  m_pcontext.reset(new seal::SEALContext(params));
  m_pevaluator = std::make_shared<seal::Evaluator>(*m_pcontext);
  m_pbatch_encoder = std::make_shared<seal::BatchEncoder>(*m_pcontext);
  m_pencryptor = std::make_shared<seal::Encryptor>(*m_pcontext, m_public_key);
}

SealBFVKernelExecutor::~SealBFVKernelExecutor() {
  m_pencryptor.reset();
  m_pbatch_encoder.reset();
  m_pevaluator.reset();
}

void SealBFVKernelExecutor::matchLevel(seal::Ciphertext* a,
                                       seal::Ciphertext* b) const {
  int a_level = getLevel(*a);
  int b_level = getLevel(*b);
  if (a_level > b_level)
    m_pevaluator->mod_switch_to_inplace(*a, b->parms_id());
  else if (a_level < b_level)
    m_pevaluator->mod_switch_to_inplace(*b, a->parms_id());
}

std::vector<seal::Ciphertext> SealBFVKernelExecutor::dotPlainBatchAxis(
    const std::vector<seal::Ciphertext>& arg1,
    const std::vector<seal::Plaintext>& arg2, size_t dim0, size_t dim1,
    size_t dim2) {
  if (arg1.size() != dim0 * dim1) {
    throw std::runtime_error("DotPlainBatchAxis arg1 wrong shape");
  }
  if (arg2.size() != dim1 * dim2) {
    throw std::runtime_error("DotPlainBatchAxis arg2 wrong shape");
  }

  std::vector<seal::Ciphertext> out(dim0 * dim2);
#pragma omp parallel for collapse(2) \
    num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t out_ind0 = 0; out_ind0 < dim0; ++out_ind0) {
    for (size_t out_ind1 = 0; out_ind1 < dim2; ++out_ind1) {
      size_t out_idx = colMajorIndex(dim0, dim2, out_ind0, out_ind1);
      for (size_t inner_dim = 0; inner_dim < dim1; inner_dim++) {
        size_t arg1_idx = colMajorIndex(dim0, dim1, out_ind0, inner_dim);
        size_t arg2_idx = colMajorIndex(dim1, dim2, inner_dim, out_ind1);
        if (inner_dim == 0) {
          m_pevaluator->multiply_plain(arg1[arg1_idx], arg2[arg2_idx],
                                       out[out_idx]);
          continue;
        }
        seal::Ciphertext tmp;
        m_pevaluator->multiply_plain(arg1[arg1_idx], arg2[arg2_idx], tmp);
        m_pevaluator->add_inplace(out[out_idx], tmp);
      }
    }
  }
  return out;
}

std::vector<seal::Ciphertext> SealBFVKernelExecutor::dotCipherBatchAxis(
    const std::vector<seal::Ciphertext>& arg1,
    const std::vector<seal::Ciphertext>& arg2, size_t dim0, size_t dim1,
    size_t dim2) {
  if (arg1.size() != dim0 * dim1) {
    throw std::runtime_error("DotCipherBatchAxis arg1 wrong shape");
  }
  if (arg2.size() != dim1 * dim2) {
    throw std::runtime_error("DotCipherBatchAxis arg2 wrong shape");
  }

  std::vector<seal::Ciphertext> out(dim0 * dim2);
#pragma omp parallel for collapse(2) \
    num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t out_ind0 = 0; out_ind0 < dim0; ++out_ind0) {
    for (size_t out_ind1 = 0; out_ind1 < dim2; ++out_ind1) {
      size_t out_idx = colMajorIndex(dim0, dim2, out_ind0, out_ind1);
      for (size_t inner_dim = 0; inner_dim < dim1; inner_dim++) {
        size_t arg1_idx = colMajorIndex(dim0, dim1, out_ind0, inner_dim);
        size_t arg2_idx = colMajorIndex(dim1, dim2, inner_dim, out_ind1);

        if (inner_dim == 0) {
          m_pevaluator->multiply(arg1[arg1_idx], arg2[arg2_idx], out[out_idx]);
          m_pevaluator->relinearize_inplace(out[out_idx], m_relin_keys);
          continue;
        }
        seal::Ciphertext tmp;
        m_pevaluator->multiply(arg1[arg1_idx], arg2[arg2_idx], tmp);
        m_pevaluator->relinearize_inplace(tmp, m_relin_keys);
        m_pevaluator->add_inplace(out[out_idx], tmp);
      }
    }
  }
  return out;
}

seal::Ciphertext SealBFVKernelExecutor::accumulate(
    const seal::Ciphertext& cipher_input, std::size_t count) {
  seal::Ciphertext retval;
  if (count > 0) {
    retval = cipher_input;
    auto max_steps = (1 << seal::util::get_significant_bit_count(count));
    for (int steps = 1; steps < max_steps; steps <<= 1) {
      seal::Ciphertext rotated;
      m_pevaluator->rotate_rows(retval, steps, m_galois_keys, rotated,
                                seal::MemoryPoolHandle::ThreadLocal());
      m_pevaluator->add_inplace(retval, rotated);
    }
  } else {
    m_pencryptor->encrypt_zero(retval);
  }

  return retval;
}

std::vector<std::vector<seal::Ciphertext>> SealBFVKernelExecutor::matMulVal(
    const std::vector<seal::Ciphertext>& A,
    const std::vector<seal::Ciphertext>& B_T, size_t dim1, size_t dim2,
    size_t dim3) {
  std::vector<std::vector<seal::Ciphertext>> out(
      dim1, std::vector<seal::Ciphertext>(dim3));

#pragma omp parallel for collapse(2) \
    num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < dim1; i++) {
    for (size_t j = 0; j < dim3; j++) {
      m_pevaluator->multiply(A[i], B_T[j], out[i][j]);
      m_pevaluator->relinearize_inplace(out[i][j], m_relin_keys);

      out[i][j] = accumulate(out[i][j], dim2);
    }
  }
  return out;
}

std::vector<seal::Ciphertext> SealBFVKernelExecutor::matMulRow(
    const std::vector<seal::Ciphertext>& A, const seal::Ciphertext& B,
    size_t dim1, size_t dim2, size_t dim3) {
  std::vector<seal::Ciphertext> out(A.size());

  std::vector<seal::Ciphertext> vec_ct_res(A.size());

  size_t slot_count = m_pbatch_encoder->slot_count();
  size_t row_size = slot_count / 2;

  // Spacing is based on the number of Rows in Matrix B (or Columns in A)
  size_t spacers = row_size / dim2;

  std::mutex mtx;

#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < A.size(); i++) {
    m_pevaluator->multiply(A[i], B, vec_ct_res[i]);
    m_pevaluator->relinearize_inplace(vec_ct_res[i], m_relin_keys);

    // Rotating by step * spacer
    out[i] = vec_ct_res[i];
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
    for (size_t j = 1; j < dim2; j++) {
      seal::Ciphertext rotated;
      m_pevaluator->rotate_rows(vec_ct_res[i], j * spacers, m_galois_keys,
                                rotated, seal::MemoryPoolHandle::ThreadLocal());
      {
        std::lock_guard<std::mutex> lock(mtx);
        m_pevaluator->add_inplace(out[i], rotated);
      }
    }
  }
  return out;
}

}  // namespace heseal
}  // namespace he
}  // namespace intel
