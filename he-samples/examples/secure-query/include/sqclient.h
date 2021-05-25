// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <memory>
#include <string>
#include <vector>

#include "seal/seal.h"
#include "sq_helper_functions.h"
#include "sq_types.h"

class SQClient {
 public:
  SQClient();

  void initializeSealContext(
      size_t _polymodulus_degree, size_t _plaintext_modulus,
      std::vector<seal::Modulus> coeff_modulus = std::vector<seal::Modulus>());

  void initializeSealContextInteractive();

  seal::EncryptionParameters sealParams() const;

  seal::PublicKey* publicKey() const;
  seal::RelinKeys* relinKeys() const;
  size_t keyLength() const;
  seal::Encryptor* encryptor() const;
  std::vector<seal::Ciphertext> encodeStringQuery(const std::string& query);
  std::string decodeToString(seal::Ciphertext cipher1);

 private:
  size_t determineMaxKeyLengthForCurrentContext();
  bool isKeyLengthValid(int key_length);
  size_t m_key_length;
  seal::EncryptionParameters m_seal_params;
  std::shared_ptr<seal::SEALContext*> m_context;
  seal::KeyGenerator* m_keygen;
  seal::PublicKey* m_public_key;
  seal::SecretKey* m_secret_key;
  seal::RelinKeys* m_relin_keys;
  seal::Encryptor* m_encryptor;
  seal::Decryptor* m_decryptor;
};
