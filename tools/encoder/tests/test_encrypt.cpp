// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include "../encrypt.h"

namespace {

using hekit::coder::Coder;
using hekit::coder::FractionalParams;
using hekit::coder::SparsePoly;
using hekit::coder::SparsePolyToZZX;
using hekit::coder::ZZXToSparsePoly;

class SingleNumFracEncrypted : public testing::TestWithParam<double> {};

TEST(SparsePolyToZZX, testSparsePolyToZZXConversion) {
  auto original = SparsePoly({{1, 2}, {3, 4}});
  const auto decoded = ZZXToSparsePoly(SparsePolyToZZX(original));
  ASSERT_EQ(decoded, original);
}

TEST_P(SingleNumFracEncrypted, testEncryptDecrypt) {
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

INSTANTIATE_TEST_SUITE_P(variousSingleNumbers, SingleNumFracEncrypted,
                         // zero, integer_part, double
                         ::testing::Values(0, 546, 546.789, 23.456, 0.2345));
}  // namespace
