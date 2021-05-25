// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once
#include <memory>
#include <string>
#include <vector>

#include "seal/seal.h"
#include "sq_helper_functions.h"
#include "sq_types.h"

class SQServer {
 public:
  SQServer();
  void initializeSealContext(size_t _polymodulus_degree,
                             size_t _plaintext_modulus);
  void createSealContextFromParameters(seal::EncryptionParameters _params);
  void setPublicKey(const seal::PublicKey& public_key);
  void setEncryptedDatabase(
      const std::vector<EncryptedDatabaseEntry>& encrypted_database);
  void setDatabase(const std::vector<DatabaseEntry>& db);
  void createEncryptedDatabaseFromCSVFile(std::string filename);
  size_t keyLength() const;
  void setKeyLength(const size_t& keyLength);
  seal::Ciphertext queryDatabaseForMatchingEntry(
      std::vector<seal::Ciphertext> query_key, seal::RelinKeys relin_keys);

 private:
  void createPlain1CT();
  seal::Ciphertext generateComparisonMaskUsingFLT(
      const seal::Ciphertext& cipher1, const seal::Ciphertext& cipher2,
      seal::RelinKeys relin_keys);

  size_t m_key_length;
  bool m_encryption_enabled = false;
  seal::PublicKey m_public_key;
  seal::EncryptionParameters m_seal_params;
  std::shared_ptr<seal::SEALContext*> m_context;
  seal::Encryptor* m_encryptor;
  seal::Evaluator* m_evaluator;
  std::vector<EncryptedDatabaseEntry> m_encrypted_database;
  bool m_bplain1_created = false;
  seal::Ciphertext m_plain_1_ct;
};
