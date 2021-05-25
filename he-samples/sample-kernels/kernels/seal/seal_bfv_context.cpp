// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "kernels/seal/seal_bfv_context.h"

#include <seal/seal.h>

#include <memory>
#include <vector>

namespace intel {
namespace he {
namespace heseal {

std::vector<seal::Plaintext> SealBFVContext::encodeVector(
    const gsl::span<const uint64_t>& values, size_t batch_size) {
  size_t total_chunks =
      values.size() / batch_size + (values.size() % batch_size == 0 ? 0 : 1);
  size_t last_chunk_size =
      values.size() % batch_size == 0 ? batch_size : values.size() % batch_size;

  std::vector<seal::Plaintext> ret(total_chunks);
#pragma omp parallel for
  for (size_t i = 0; i < total_chunks; ++i) {
    size_t actual_chunk_size =
        (i == total_chunks - 1) ? last_chunk_size : batch_size;
    gsl::span data_chunk(&values[i * batch_size], actual_chunk_size);
    m_batch_encoder->encode(data_chunk, ret[i]);
  }
  return ret;
}

std::vector<uint64_t> SealBFVContext::decodeVector(
    const std::vector<seal::Plaintext>& plain, size_t batch_size) {
  std::vector<uint64_t> ret(plain.size() * batch_size);
#pragma omp parallel for
  for (std::size_t i = 0; i < plain.size(); ++i) {
    std::vector<uint64_t> tmp;
    m_batch_encoder->decode(plain[i], tmp);
    for (size_t j = 0; j < batch_size; ++j) {
      ret[i * batch_size + j] = tmp[j];
    }
  }
  return ret;
}

std::vector<seal::Ciphertext> SealBFVContext::encryptVector(
    const std::vector<seal::Plaintext>& plain) {
  std::vector<seal::Ciphertext> ret(plain.size());
#pragma omp parallel for
  for (std::size_t i = 0; i < plain.size(); ++i)
    m_encryptor->encrypt(plain[i], ret[i]);
  return ret;
}

std::vector<seal::Plaintext> SealBFVContext::decryptVector(
    const std::vector<seal::Ciphertext>& cipher) {
  std::vector<seal::Plaintext> ret(cipher.size());
#pragma omp parallel for
  for (std::size_t i = 0; i < cipher.size(); ++i)
    m_decryptor->decrypt(cipher[i], ret[i]);
  return ret;
}

}  // namespace heseal
}  // namespace he
}  // namespace intel
