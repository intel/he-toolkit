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

  /**
   * @brief initializeSealContextInteractive queries the user for desired encryption parameters and then varifies that
   * the parameter combination is valid. If parameters are not valid then it will request a new set of parameters.
   */
  void initializeSealContextInteractive();
  seal::EncryptionParameters sealParams() const;
  seal::PublicKey* publicKey() const;
  seal::RelinKeys* relinKeys() const;
  size_t keyLength() const;
  seal::Encryptor* encryptor() const;
  /**
   * @brief encodeStringQuery converts an std::string to a 4-bit encoded/encrypted vector of ciphertexts. See the README for details on this encoding.
   * @param query an std::string to be encoded/encrypted.
   * @return a vector of ciphertexts containing values in the range [0,7] representing the value of each character in query as 2 ciphertexts.
   */
  std::vector<seal::Ciphertext> encodeStringQuery(const std::string& query);
  /**
   * @brief decodeToString converts a ciphertext containing a 4-bit encoded string stored as coefficients into an std::string. This is the return type from calls
   * to queryDatabaseForMatchingEntry
   * @param cipher1 A ciphertext for which the plaintext coefficient values are used to store a 4-bit encoded character string
   * @return an std::string containing the decoded string value contained in cipher1
   */
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
