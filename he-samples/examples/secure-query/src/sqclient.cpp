// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "sqclient.h"

SQClient::SQClient()
    : m_key_length{0},
      m_keygen{nullptr},
      m_public_key{nullptr},
      m_secret_key{nullptr},
      m_relin_keys{nullptr},
      m_encryptor{nullptr},
      m_decryptor{nullptr} {}

void SQClient::initializeSealContext(size_t _polymodulus_degree,
                                     size_t _plaintext_modulus,
                                     std::vector<seal::Modulus> coeff_modulus) {
  if (coeff_modulus.size() == 0) {
    coeff_modulus = seal::CoeffModulus::BFVDefault(_polymodulus_degree);
  }
  m_key_length = 8;
  size_t poly_modulus_degree = _polymodulus_degree;
  size_t plain_modulus = _plaintext_modulus;

  seal::EncryptionParameters parameters(seal::scheme_type::bfv);
  parameters.set_poly_modulus_degree(poly_modulus_degree);
  parameters.set_coeff_modulus(coeff_modulus);
  seal::Modulus seal_plain_modulus = plain_modulus;
  parameters.set_plain_modulus(seal_plain_modulus);
  auto m_context = seal::SEALContext(parameters);
  m_seal_params = parameters;

  m_keygen = new seal::KeyGenerator(m_context);
  m_public_key = new seal::PublicKey();
  m_keygen->create_public_key(*m_public_key);
  m_secret_key = new seal::SecretKey(m_keygen->secret_key());
  m_relin_keys = new seal::RelinKeys();
  m_keygen->create_relin_keys(*m_relin_keys);
  m_encryptor = new seal::Encryptor(m_context, *m_public_key);
  m_decryptor = new seal::Decryptor(m_context, *m_secret_key);
}

void SQClient::initializeSealContextInteractive() {
  bool valid_config = false;

  while (!valid_config) {
    do {
      size_t poly_modulus_degree = 13;
      size_t plain_modulus = 17;
      std::cout << "Input poly modulus degree 2^x[13]: ";
      std::string poly_modulus_degree_str;
      std::getline(std::cin, poly_modulus_degree_str);
      if (poly_modulus_degree_str != "") {
        poly_modulus_degree = std::stoi(poly_modulus_degree_str);
      }
      std::cout << "Input plain modulus(most be prime and > 17)[17]: ";
      std::string plain_modulus_str;
      std::getline(std::cin, plain_modulus_str);
      if (plain_modulus_str != "") {
        plain_modulus = std::stoi(plain_modulus_str);
      }

      seal::EncryptionParameters parameters(seal::scheme_type::bfv);
      parameters.set_poly_modulus_degree(pow(2, poly_modulus_degree));
      parameters.set_coeff_modulus(
          seal::CoeffModulus::BFVDefault(pow(2, poly_modulus_degree)));
      seal::Modulus seal_plain_modulus = plain_modulus;
      parameters.set_plain_modulus(seal_plain_modulus);
      m_context = std::make_shared<seal::SEALContext*>(
          new seal::SEALContext(parameters));
      m_seal_params = parameters;
      if (m_context == nullptr) {
        std::cout << "Chosen polymodulus degree or plain modulus are not valid";
      }
    } while (m_context == nullptr);

    size_t key_length = 8;
    std::cout << "Input database key length in characters[8]: ";
    std::string key_length_str;
    std::getline(std::cin, key_length_str);
    if (key_length_str != "") {
      key_length = std::stoi(key_length_str);
    }

    bool valid_key = isKeyLengthValid(key_length);
    if (valid_key) {
      m_key_length = key_length;
      valid_config = true;
      std::cout << "Configuration is valid" << std::endl;
    } else {
      std::cout << "Chosen key length is not valid with current poly modulus "
                   "degree and plain modulus combination"
                << std::endl;
    }
  }

  m_keygen = new seal::KeyGenerator(**m_context);
  m_public_key = new seal::PublicKey();
  m_keygen->create_public_key(*m_public_key);
  m_secret_key = new seal::SecretKey(m_keygen->secret_key());
  m_relin_keys = new seal::RelinKeys();
  m_keygen->create_relin_keys(*m_relin_keys);

  m_encryptor = new seal::Encryptor(**m_context, *m_public_key);
  m_decryptor = new seal::Decryptor(**m_context, *m_secret_key);
}

seal::EncryptionParameters SQClient::sealParams() const {
  return m_seal_params;
}

seal::PublicKey* SQClient::publicKey() const { return m_public_key; }

seal::RelinKeys* SQClient::relinKeys() const { return m_relin_keys; }

size_t SQClient::keyLength() const { return m_key_length; }

seal::Encryptor* SQClient::encryptor() const { return m_encryptor; }

std::vector<seal::Ciphertext> SQClient::encodeStringQuery(
    const std::string& query) {
  std::vector<seal::Ciphertext> enc_query;
  // Encrypt the key
  enc_query.resize(m_key_length * 2);
  for (size_t x = 0; x < m_key_length; x++) {
    if (x < query.length()) {
      seal::Plaintext key_high;
      seal::Plaintext key_low;
      key_high.resize(m_seal_params.poly_modulus_degree());
      key_low.resize(m_seal_params.poly_modulus_degree());
      key_high = query[x] >> 4;
      key_low = query[x] & 15;
      m_encryptor->encrypt(key_high, enc_query[x * 2]);
      m_encryptor->encrypt(key_low, enc_query[x * 2 + 1]);
    } else {
      m_encryptor->encrypt_zero(enc_query[x * 2]);
      m_encryptor->encrypt_zero(enc_query[x * 2 + 1]);
    }
  }

  return enc_query;
}

std::string SQClient::decodeToString(seal::Ciphertext cipher1) {
  seal::Plaintext result_values_pt;
  m_decryptor->decrypt(cipher1, result_values_pt);

  std::vector<unsigned int> database_value =
      sq::decodePlaintextToEncodedVector(result_values_pt);
  std::string database_string = sq::decodeHexVectorToString(database_value);
  return database_string;
}

size_t SQClient::determineMaxKeyLengthForCurrentContext() {
  int key_size = 1;
  while (isKeyLengthValid(key_size)) {
    key_size++;
  }

  return key_size;
}

bool SQClient::isKeyLengthValid(int key_length) {
  seal::KeyGenerator keygen = seal::KeyGenerator(**m_context);
  seal::PublicKey public_key = seal::PublicKey();
  keygen.create_public_key(public_key);
  seal::SecretKey secret_key = seal::SecretKey(keygen.secret_key());
  seal::RelinKeys relin_keys = seal::RelinKeys();
  keygen.create_relin_keys(relin_keys);

  seal::Encryptor encryptor = seal::Encryptor(**m_context, public_key);
  seal::Evaluator evaluator = seal::Evaluator(**m_context);
  seal::Decryptor decryptor = seal::Decryptor(**m_context, secret_key);

  seal::Ciphertext result;

  seal::Ciphertext one;
  encryptor.encrypt_zero(one);

  std::vector<seal::Ciphertext> query_vector_test;
  query_vector_test.push_back(one);

  for (int x = 0; x < key_length * 2; x++) {
    seal::Ciphertext zero;
    encryptor.encrypt_zero(zero);
    query_vector_test.push_back(zero);

    seal::Ciphertext m;
    encryptor.encrypt_zero(m);
    evaluator.sub_inplace(query_vector_test.back(), m);
    evaluator.exponentiate_inplace(query_vector_test.back(),
                                   m_seal_params.plain_modulus().value() - 1,
                                   relin_keys);
    evaluator.negate_inplace(query_vector_test.back());
    evaluator.add_inplace(query_vector_test.back(), one);
  }

  evaluator.multiply_many(query_vector_test, relin_keys, result);
  int noise_budget = decryptor.invariant_noise_budget(result);

  return (noise_budget > 0);
}
