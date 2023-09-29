// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include "../encrypt.h"

namespace {

using hekit::coder::BalancedParams;
using hekit::coder::BalancedSlotsParams;
using hekit::coder::Coder;
using hekit::coder::FractionalParams;
using hekit::coder::SparsePoly;
using hekit::coder::SparsePolyToZZX;
using hekit::coder::ZZXToSparsePoly;

class SingleNumEncrypted : public testing::TestWithParam<double> {};

TEST(SparsePolyToZZX, testSparsePolyToZZXConversion) {
  auto original = SparsePoly({{1, 2}, {3, 4}});
  const auto decoded = ZZXToSparsePoly(SparsePolyToZZX(original));
  ASSERT_EQ(decoded, original);
}

TEST_P(SingleNumEncrypted, testFractionalEncryptDecrypt) {
  // TODO Move out
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params =
      FractionalParams{.rw = 1.2, .epsil = 1e-8, .frac_degree = 4096};
  Coder coder(params);
  double original = GetParam();

  const auto encoded = coder.encode(original);

  ASSERT_NEAR(original, coder.decode(encoded), params.epsil);

  const auto encrypted = encrypt(encoded, pk);
  const auto decrypted = decrypt(encrypted, sk);

  ASSERT_EQ(encoded.poly(), decrypted.poly())
      << "Encoded Poly: " << encoded.poly().toString() << "\n"
      << "Decrypted Poly: " << decrypted.poly().toString() << "\n";

  double decoded = coder.decode(decrypted);

  ASSERT_NEAR(original, decoded, params.epsil);
}

TEST_P(SingleNumEncrypted, testBalancedEncryptDecrypt) {
  // TODO Move out
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params = BalancedParams{.rw = 1.2, .epsil = 1e-8};
  Coder coder(params);
  double original = GetParam();

  const auto encoded = coder.encode(original);

  ASSERT_NEAR(original, coder.decode(encoded), params.epsil);

  const auto encrypted = encrypt(encoded, pk);
  const auto decrypted = decrypt(encrypted, sk);

  ASSERT_EQ(encoded.poly(), decrypted.poly())
      << "Encoded Poly: " << encoded.poly().toString() << "\n"
      << "Decrypted Poly: " << decrypted.poly().toString() << "\n";

  double decoded = coder.decode(decrypted);

  ASSERT_NEAR(original, decoded, params.epsil);
}

TEST(EncryptedNums, testBalancedSlotsEncryptDecrypt) {
  // TODO Move out
  //  47                  4096                73734                24576 6 47
  //  500                 15000                 4000                  8
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(15000L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params = BalancedSlotsParams{.rw = 1.2, .epsil = 1e-8};
  Coder coder(params);
  // TODO parametrize
  std::vector<double> original = {0.0, 2.2, 109.8, 453.756};
  original.resize(sk.getContext().getNSlots());

  const auto encoded = coder.encode(original);
  const auto encrypted = encrypt(encoded, pk);
  const auto decrypted = decrypt(encrypted, sk);

  ASSERT_EQ(encoded.poly(), decrypted.poly())
      << "Encoded Poly: " << encoded.poly().toString() << "\n"
      << "Decrypted Poly: " << decrypted.poly().toString() << "\n";

  const auto decoded = coder.decode(decrypted);

  for (long i = 0; i < original.size(); ++i)
    ASSERT_NEAR(original[i], decoded[i], params.epsil);
}

INSTANTIATE_TEST_SUITE_P(variousSingleNumbers, SingleNumEncrypted,
                         // zero, integer_part, double
                         ::testing::Values(0, 546, 546.789, 23.456, 0.2345));
}  // namespace
