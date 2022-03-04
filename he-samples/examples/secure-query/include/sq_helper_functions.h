// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_SECURE_QUERY_INCLUDE_SQ_HELPER_FUNCTIONS_H_
#define HE_SAMPLES_EXAMPLES_SECURE_QUERY_INCLUDE_SQ_HELPER_FUNCTIONS_H_
#include <fstream>
#include <string>
#include <vector>

#include "sq_types.h"

namespace sq {

static inline std::vector<unsigned int> encodeStringToHexVector(
    const std::string& value, const unsigned int length) {
  std::vector<unsigned int> encoded_values;

  const unsigned int vector_len = length / 2;
  for (unsigned int x = 0; x < vector_len; x++) {
    if (x < value.length()) {
      char high = value[x] >> 4;
      char low = value[x] & 15;
      encoded_values.push_back(high);
      encoded_values.push_back(low);
    } else {
      encoded_values.push_back(0);
      encoded_values.push_back(0);
    }
  }
  return encoded_values;
}

static inline std::string decodeHexVectorToString(
    const std::vector<unsigned int>& vec) {
  std::vector<char> c_str;
  for (unsigned int x = 0; x < vec.size(); x += 2) {
    char character = static_cast<char>(((vec[x] << 4) | vec[x + 1]));
    c_str.push_back(character);
  }
  return std::string(c_str.data(), c_str.size());
}

static inline seal::Plaintext writeEncodedStringToPlaintext(
    const std::vector<unsigned int>& encoded_string,
    unsigned int poly_modulus_degree) {
  seal::Plaintext encoded_pt;
  encoded_pt.resize(poly_modulus_degree);
  for (unsigned int x = 0; x < poly_modulus_degree; x++) {
    encoded_pt[x] = 0;
  }

  for (unsigned int x = 0; x < encoded_string.size(); x++) {
    encoded_pt[x] = encoded_string[x];
  }
  return encoded_pt;
}

static inline std::vector<unsigned int> decodePlaintextToEncodedVector(
    const seal::Plaintext& value) {
  std::vector<unsigned int> decoded_values;
  for (unsigned int x = 0; x < value.coeff_count(); x++) {
    decoded_values.push_back(value[x]);
  }
  // Handle special case where return result is 0
  if (decoded_values.size() == 1) decoded_values.push_back(0);
  return decoded_values;
}

inline static std::vector<DatabaseEntry> createDatabaseFromCSVFile(
    std::string filename) {
  std::vector<DatabaseEntry> db;
  std::ifstream input_file;
  input_file.open(filename);
  if (!input_file.is_open()) {
    throw std::runtime_error(
        "Error: Failed to open file \"" + filename +
        "\"\n       Please check the file exists and the path is correct.");
  } else {
    std::string next_line;
    while (std::getline(input_file, next_line)) {
      auto cut_point = next_line.find(",");
      if (cut_point != std::string::npos) {
        std::string key = next_line.substr(0, cut_point);
        std::string value =
            next_line.substr(cut_point + 1, next_line.length() - cut_point + 1);
        db.push_back(DatabaseEntry(key, value));
      }
    }
  }
  return db;
}

static inline std::vector<EncryptedDatabaseEntry> encryptDatabase(
    const std::vector<DatabaseEntry>& db, const seal::Encryptor* m_encryptor,
    int poly_mod_degree, size_t key_length) {
  std::vector<EncryptedDatabaseEntry> encrypted_db;
  encrypted_db.reserve(db.size());
#pragma omp parallel for
  for (unsigned int x = 0; x < db.size(); x++) {
    const DatabaseEntry& db_entry = db[x];
    EncryptedDatabaseEntry enc_db_entry;

    // Encrypt the key
    enc_db_entry.key.resize(key_length * 2);
    for (size_t x = 0; x < key_length; x++) {
      if (x < db_entry.key.length()) {
        seal::Plaintext key_high;
        seal::Plaintext key_low;
        key_high.resize(poly_mod_degree);
        key_low.resize(poly_mod_degree);
        key_high = db_entry.key[x] >> 4;
        key_low = db_entry.key[x] & 15;
        m_encryptor->encrypt(key_high, enc_db_entry.key[x * 2]);
        m_encryptor->encrypt(key_low, enc_db_entry.key[x * 2 + 1]);
      } else {
        m_encryptor->encrypt_zero(enc_db_entry.key[x * 2]);
        m_encryptor->encrypt_zero(enc_db_entry.key[x * 2 + 1]);
      }
    }

    // Encrypt the value string
    auto enc_vec = encodeStringToHexVector(db_entry.value, poly_mod_degree);
    m_encryptor->encrypt(
        writeEncodedStringToPlaintext(enc_vec, poly_mod_degree),
        enc_db_entry.value);
#pragma omp critical
    encrypted_db.push_back(enc_db_entry);
  }
  return encrypted_db;
}

}  // namespace sq

#endif  // HE_SAMPLES_EXAMPLES_SECURE_QUERY_INCLUDE_SQ_HELPER_FUNCTIONS_H_
