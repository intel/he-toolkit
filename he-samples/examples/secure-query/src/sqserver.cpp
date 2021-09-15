// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "sqserver.h"

SQServer::SQServer() {}

void SQServer::initializeSealContext(size_t _polymodulus_degree,
                                     size_t _plaintext_modulus) {
  size_t poly_modulus_degree = _polymodulus_degree;
  size_t plain_modulus = _plaintext_modulus;

  seal::EncryptionParameters parameters(seal::scheme_type::bfv);
  parameters.set_poly_modulus_degree(poly_modulus_degree);
  parameters.set_coeff_modulus(
      seal::CoeffModulus::BFVDefault(poly_modulus_degree));
  seal::Modulus seal_plain_modulus = plain_modulus;
  parameters.set_plain_modulus(seal_plain_modulus);
  m_context =
      std::make_shared<seal::SEALContext*>(new seal::SEALContext(parameters));
  m_evaluator = new seal::Evaluator(**m_context);
}

void SQServer::createSealContextFromParameters(
    seal::EncryptionParameters _params) {
  m_seal_params = _params;
  m_context =
      std::make_shared<seal::SEALContext*>(new seal::SEALContext(_params));
  m_evaluator = new seal::Evaluator(**m_context);
}

void SQServer::setPublicKey(const seal::PublicKey& public_key) {
  m_public_key = public_key;
  m_encryptor = new seal::Encryptor(**m_context, public_key);
  m_encryption_enabled = true;
}

void SQServer::setEncryptedDatabase(
    const std::vector<EncryptedDatabaseEntry>& encrypted_database) {
  m_encrypted_database = encrypted_database;
}

size_t SQServer::keyLength() const { return m_key_length; }

void SQServer::setKeyLength(const size_t& key_length) {
  m_key_length = key_length;
}

seal::Ciphertext SQServer::queryDatabaseForMatchingEntry(
    std::vector<seal::Ciphertext> query_key, seal::RelinKeys relin_keys) {
  createPlain1CT();

  seal::Ciphertext mult_accumulate;
  m_encryptor->encrypt_zero(mult_accumulate);
  /* For each entry in the encrypted database we perform a comparison between the
   * query key and entry key which evaluates to 1 if the query and entry match or
   * 0 if they differ. This result is then multipled against the encrypted value
   * ciphertext which is then added to the return ciphertext.
   */
#pragma omp parallel for
  for (unsigned int entry = 0; entry < m_encrypted_database.size(); entry++) {
    const EncryptedDatabaseEntry& enc_db_entry = m_encrypted_database[entry];
    seal::Ciphertext combined_mask;
    m_encryptor->encrypt_zero(combined_mask);
    m_evaluator->add_inplace(combined_mask, m_plain_1_ct);
    std::vector<seal::Ciphertext> masks;
    masks.reserve(enc_db_entry.key.size() + 1);
    for (size_t x = 0; x < enc_db_entry.key.size(); x++) {
      //We add the results of the comparison between all of the component elements of the query and key.
      masks.push_back(generateComparisonMaskUsingFLT(enc_db_entry.key[x],
                                                     query_key[x], relin_keys));
    }
    seal::Ciphertext return_values;
    masks.push_back(enc_db_entry.value);
    /*
     * Masks contains the results of comparing each 4 bit element of the query
     * key against the key for a database entry plus the db_entry value. This
     * results in the following computation being performed
     * (mask[0])*(mask[1]*...*(mask[max_key_length])*(db_entry.value)
     * The result of this computation is db_entry.value if all values of the
     * db_entry.key match the query, else the result is 0
     *
     */
    m_evaluator->multiply_many(masks, relin_keys, return_values);
    /* We enforce that all key values in the database are unique. Thus we can
     * return the result of the query by adding the results from all of the
     * key/value multiplications performend previously. If we had 3 values and
     * key 1 matched the query the resultant computation would look like the following
     * 0 + key[1].value + 0 = key[1].value
     */
#pragma omp critical
    m_evaluator->add_inplace(mult_accumulate, return_values);
  }
  return mult_accumulate;
}

void SQServer::createPlain1CT() {
  if (m_bplain1_created == false) {
    seal::Plaintext plain_1;
    plain_1.resize(m_seal_params.poly_modulus_degree());
    for (unsigned int x = 1; x < plain_1.capacity(); x++) plain_1[x] = 0;

    plain_1[0] = 1;

    m_encryptor->encrypt(plain_1, m_plain_1_ct);
    m_bplain1_created = true;
  }

  return;
}
seal::Ciphertext SQServer::generateComparisonMaskUsingFLT(
    const seal::Ciphertext& cipher1, const seal::Ciphertext& cipher2,
    seal::RelinKeys relin_keys) {
  seal::Ciphertext mask;
  m_evaluator->sub(cipher1, cipher2, mask);
  m_evaluator->exponentiate_inplace(
      mask, m_seal_params.plain_modulus().value() - 1, relin_keys);
  m_evaluator->negate_inplace(mask);
  m_evaluator->add_inplace(mask, m_plain_1_ct);
  return mask;
}
