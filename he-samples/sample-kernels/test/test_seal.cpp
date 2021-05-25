// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>
#include <seal/seal.h>

#include <memory>
#include <vector>

#include "test_util.h"

namespace intel {
namespace he {
namespace heseal {

TEST(seal_example, seal_ckks_basics) {
  seal::EncryptionParameters parms(seal::scheme_type::ckks);
  size_t poly_modulus_degree = 8192;
  parms.set_poly_modulus_degree(poly_modulus_degree);
  parms.set_coeff_modulus(
      seal::CoeffModulus::Create(poly_modulus_degree, {60, 40, 40, 60}));

  auto context = seal::SEALContext(parms);
  // print_parameters(context);

  seal::KeyGenerator keygen(context);
  seal::PublicKey public_key;
  keygen.create_public_key(public_key);
  auto secret_key = keygen.secret_key();
  seal::RelinKeys relin_keys;
  keygen.create_relin_keys(relin_keys);

  seal::Encryptor encryptor(context, public_key);
  seal::Evaluator evaluator(context);
  seal::Decryptor decryptor(context, secret_key);
  seal::CKKSEncoder encoder(context);

  std::vector<double> input{0.0, 1.1, 2.2, 3.3};

  seal::Plaintext plain;
  double scale = pow(2.0, 40);
  encoder.encode(input, scale, plain);

  seal::Ciphertext encrypted;
  encryptor.encrypt(plain, encrypted);

  evaluator.square_inplace(encrypted);
  evaluator.relinearize_inplace(encrypted, relin_keys);
  decryptor.decrypt(encrypted, plain);
  encoder.decode(plain, input);

  evaluator.mod_switch_to_next_inplace(encrypted);

  decryptor.decrypt(encrypted, plain);

  encoder.decode(plain, input);

  encrypted.scale() *= 3;
  decryptor.decrypt(encrypted, plain);
  encoder.decode(plain, input);
}

TEST(seal_example, seal_ckks_complex_conjugate) {
  seal::EncryptionParameters parms(seal::scheme_type::ckks);
  size_t poly_modulus_degree = 8192;
  parms.set_poly_modulus_degree(poly_modulus_degree);
  parms.set_coeff_modulus(
      seal::CoeffModulus::Create(poly_modulus_degree, {60, 40, 40, 60}));

  auto context = seal::SEALContext(parms);
  // print_parameters(context);

  seal::KeyGenerator keygen(context);
  seal::PublicKey public_key;
  keygen.create_public_key(public_key);
  auto secret_key = keygen.secret_key();
  seal::RelinKeys relin_keys;
  keygen.create_relin_keys(relin_keys);
  seal::GaloisKeys galois_keys;
  keygen.create_galois_keys(galois_keys);

  seal::Encryptor encryptor(context, public_key);
  seal::Evaluator evaluator(context);
  seal::Decryptor decryptor(context, secret_key);
  seal::CKKSEncoder encoder(context);

  std::vector<std::complex<double>> input{{0.0, 1.1}, {2.2, 3.3}};
  std::vector<std::complex<double>> exp_output{{0.0, -1.1}, {2.2, -3.3}};
  std::vector<std::complex<double>> output;

  seal::Plaintext plain;
  double scale = pow(2.0, 40);
  encoder.encode(input, scale, plain);

  seal::Ciphertext encrypted;
  encryptor.encrypt(plain, encrypted);
  evaluator.complex_conjugate_inplace(encrypted, galois_keys);

  decryptor.decrypt(encrypted, plain);
  encoder.decode(plain, output);

  EXPECT_TRUE(abs(exp_output[0] - output[0]) < 0.1);
  EXPECT_TRUE(abs(exp_output[1] - output[1]) < 0.1);
}

TEST(seal_example, seal_bfv_basics) {
  seal::EncryptionParameters parms(seal::scheme_type::bfv);
  size_t poly_modulus_degree = 8192;
  parms.set_poly_modulus_degree(poly_modulus_degree);
  parms.set_coeff_modulus(seal::CoeffModulus::BFVDefault(poly_modulus_degree));
  parms.set_plain_modulus(
      seal::PlainModulus::Batching(poly_modulus_degree, 20));

  auto context = seal::SEALContext(parms);
  // print_parameters(context);

  seal::KeyGenerator keygen(context);
  seal::PublicKey public_key;
  keygen.create_public_key(public_key);
  auto secret_key = keygen.secret_key();
  seal::RelinKeys relin_keys;
  keygen.create_relin_keys(relin_keys);

  seal::Encryptor encryptor(context, public_key);
  seal::Evaluator evaluator(context);
  seal::Decryptor decryptor(context, secret_key);
  seal::BatchEncoder encoder(context);
  size_t slot_count = encoder.slot_count();
  size_t n_rows = 2;  // This defined in SEAL
  size_t row_size = slot_count / n_rows;
  size_t n_slots = 4;

  auto input =
      generateVector<std::uint64_t>(slot_count, row_size, n_rows, n_slots);

  std::vector<std::uint64_t> exp_output{0ULL,  1ULL,  4ULL,  9ULL,
                                        16ULL, 25ULL, 36ULL, 49ULL};
  std::vector<std::uint64_t> output;

  seal::Plaintext plain;
  encoder.encode(input, plain);

  seal::Ciphertext encrypted;
  encryptor.encrypt(plain, encrypted);

  evaluator.square_inplace(encrypted);
  evaluator.relinearize_inplace(encrypted, relin_keys);
  decryptor.decrypt(encrypted, plain);
  encoder.decode(plain, output);

  for (size_t r = 0; r < n_rows; ++r) {
    for (size_t i = 0; i < n_slots; ++i) {
      EXPECT_EQ(exp_output[i + r * n_slots], output[i + r * row_size]);
    }
  }
}

}  // namespace heseal
}  // namespace he
}  // namespace intel
