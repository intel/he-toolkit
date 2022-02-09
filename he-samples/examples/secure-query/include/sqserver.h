// Copyright (C) 2020 Intel Corporation
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
  size_t keyLength() const;
  void setKeyLength(const size_t& keyLength);
  /**
   * @brief `queryDatabaseForMatchingEntry` compares the query key against the
   * key value of all database entries and returns a ciphertext containing the
   * entry's value if a match is found.
   * @param query_key is a vector of ciphertexts representing the encoded and
   * encrypted query key.
   * @param relin_keys used for relinearization during function execution
   * @return A ciphertext containing the encrypted value if a match is found or
   * zero if the query did not match any of the database keys.
   */
  seal::Ciphertext queryDatabaseForMatchingEntry(
      std::vector<seal::Ciphertext> query_key, seal::RelinKeys relin_keys);

 private:
  void createPlain1CT();
  /**
   * @brief `generateComparisonMaskUsingFLT` performs a comparison between
   * `cipher1` and `cipher2` that evaluates to 1 if they are same value or 0 if
   * they differ.
   *
   * This comparison is achieved by combining the property that plaintext
   * values are defined modulo the plaintext modulus and the concept from
   * Fermat's little theorem which states that if `p` is a prime and `a` is any
   * integer not divisible by `p` then `a^(p-1) = 1 % p`, where `a` is an
   * integer and `p` is the plaintext modulus. To perform this comparison
   * `cipher1` is subtracted from `cipher2` to generate a mask ciphertext. The
   * value of this mask is 0 if `cipher1` and `cipher2` are the same value or
   * some value between `(-p,-1)` or `(1,p)`. We then raise this value to `p -
   * 1` which per FLT results in the value being `1 % p = 1 iff a != 0` or `0
   * iff a = 0`. We finally negate the value and add 1, resulting in 0 for all
   * non matches and 1 for any matching case.
   * @param cipher1 contains a value between `[0,p)`.
   * @param cipher2 contains a value between `[0,p)`.
   * @param relin_keys required for exponentiating in place.
   * @return A ciphertext encoding a value of 1 if the value of `cipher1 ==
   * cipher2` or 0 if the value of `cipher1 != cipher2`.
   */
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
