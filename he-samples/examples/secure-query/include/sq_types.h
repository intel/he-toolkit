// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_SECURE_QUERY_INCLUDE_SQ_TYPES_H_
#define HE_SAMPLES_EXAMPLES_SECURE_QUERY_INCLUDE_SQ_TYPES_H_
#include <string>
#include <vector>

#include "seal/seal.h"

struct DatabaseEntry {
  DatabaseEntry(std::string _key, std::string _value) {
    key = _key;
    value = _value;
  }
  // int key;
  std::string key;
  std::string value;
};

struct EncryptedDatabaseEntry {
  std::vector<seal::Ciphertext> key;
  seal::Ciphertext value;
};

#endif  // HE_SAMPLES_EXAMPLES_SECURE_QUERY_INCLUDE_SQ_TYPES_H_
