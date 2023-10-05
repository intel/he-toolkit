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

struct Crypto {
  Crypto() = delete;
  explicit Crypto(const helib::ContextBuilder<helib::BGV>& cb)
      : context(cb.build()), sk(context), pk((sk.GenSecKey(), sk)) {}

  helib::Context context;
  helib::SecKey sk;
  const helib::PubKey& pk;
};

template <typename EncodingSchemeParams>
struct Params {
  helib::ContextBuilder<helib::BGV> context_builder;
  Coder<EncodingSchemeParams> coder;
};

struct FractionalEncryptedSingleNums
    : public testing::TestWithParam<
          std::pair<Params<FractionalParams>, std::vector<double>>> {};
struct BalancedEncryptedSingleNums
    : public testing::TestWithParam<
          std::pair<Params<BalancedParams>, std::vector<double>>> {};
// struct BalancedSlotsEncryptedSingleNums : public
// testing::TestWithParam<Params<BalancedSlotsParams>, std::vector<double>> {};

TEST(SparsePolyToZZX, testSparsePolyToZZXConversion) {
  auto original = SparsePoly({{1, 2}, {3, 4}});
  const auto decoded = ZZXToSparsePoly(SparsePolyToZZX(original));
  EXPECT_EQ(decoded, original);
}

template <typename EncodingSchemeParams>
static void testEncryptDecrypt(const EncodingSchemeParams& get_params,
                               const std::vector<double>& input_nums) {
  const auto [bgv_cb, coder] = get_params;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  for (auto const& original : input_nums) {
    const auto encoded = coder.encode(original);

    EXPECT_NEAR(original, coder.decode(encoded), params.epsil);

    const auto encrypted = encrypt(encoded, crypto.pk);
    const auto decrypted = decrypt(encrypted, crypto.sk);

    EXPECT_EQ(encoded.poly(), decrypted.poly())
        << "Encoded Poly: " << encoded.poly().toString() << "\n"
        << "Decrypted Poly: " << decrypted.poly().toString() << "\n";

    double decoded = coder.decode(decrypted);

    EXPECT_NEAR(original, decoded, params.epsil);
  }
}

TEST_P(FractionalEncryptedSingleNums, testEncryptDecrypt) {
  const auto [params, input_nums] = GetParam();
  testEncryptDecrypt(params, input_nums);
}

TEST_P(BalancedEncryptedSingleNums, testEncryptDecrypt) {
  const auto [params, input_nums] = GetParam();
  testEncryptDecrypt(params, input_nums);
}

TEST(EncryptedNums, testBalancedSlotsEncryptDecrypt) {
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

  EXPECT_EQ(encoded.poly(), decrypted.poly())
      << "Encoded Poly: " << encoded.poly().toString() << "\n"
      << "Decrypted Poly: " << decrypted.poly().toString() << "\n";

  const auto decoded = coder.decode(decrypted);

  for (long i = 0; i < original.size(); ++i)
    EXPECT_NEAR(original[i], decoded[i], params.epsil);
}

inline static std::vector<double> operator+(const std::vector<double>& nums1,
                                            const std::vector<double>& nums2) {
  if (nums1.size() != nums2.size())
    throw std::logic_error("vectors do not have equal size");
  std::vector<double> ans;
  ans.reserve(nums1.size());
  std::transform(nums1.begin(), nums1.end(), nums2.begin(), ans.begin(),
                 std::plus<double>{});
  return ans;
}

inline static std::vector<double> operator*(const std::vector<double>& nums1,
                                            const std::vector<double>& nums2) {
  if (nums1.size() != nums2.size())
    throw std::logic_error("vectors do not have equal size");
  std::vector<double> ans;
  ans.reserve(nums1.size());
  std::transform(nums1.begin(), nums1.end(), nums2.begin(), ans.begin(),
                 std::multiplies<double>{});
  return ans;
}

TEST(EncryptedNums, testFractionalAdd) {
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params =
      FractionalParams{.rw = 1.2, .epsil = 1e-8, .frac_degree = 4096L};
  Coder coder(params);
  // TODO parametrize
  double num1 = 109.8;
  double num2 = 9.02;

  const auto op = num1 + num2;

  const auto encoded1 = coder.encode(num1);
  const auto encoded2 = coder.encode(num2);
  const auto encrypted1 = encrypt(encoded1, pk);
  const auto encrypted2 = encrypt(encoded2, pk);

  const auto encrypted = encrypted1 + encrypted2;

  const auto decrypted = decrypt(encrypted, sk);
  const auto decoded = coder.decode(decrypted);

  EXPECT_NEAR(op, decoded, params.epsil);
}

TEST(EncryptedNums, testFractionalMult) {
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params =
      FractionalParams{.rw = 1.2, .epsil = 1e-8, .frac_degree = 4096L};
  Coder coder(params);
  // TODO parametrize
  double num1 = 1.1;
  double num2 = 1.0;

  const auto op = num1 * num2;

  const auto encoded1 = coder.encode(num1);
  const auto encoded2 = coder.encode(num2);
  const auto encrypted1 = encrypt(encoded1, pk);
  const auto encrypted2 = encrypt(encoded2, pk);

  const auto encrypted = encrypted1 * encrypted2;

  const auto decrypted = decrypt(encrypted, sk);
  const auto decoded = coder.decode(decrypted);

  EXPECT_NEAR(op, decoded, params.epsil * (num1 + num2));
}

TEST(EncryptedNums, testBalancedAdd) {
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  // addSome1DMatrices(sk);
  const helib::PubKey& pk = sk;
  //
  const auto params = BalancedParams{.rw = 1.2, .epsil = 1e-8};
  Coder coder(params);
  // TODO parametrize
  double num1 = 1.0;  // 109.8;
  double num2 = 1.0;  // 9.02;

  const auto op = num1 + num2;

  const auto encoded1 = coder.encode(num1);
  const auto encoded2 = coder.encode(num2);
  const auto encrypted1 = encrypt(encoded1, pk);
  const auto encrypted2 = encrypt(encoded2, pk);

  const auto encrypted = encrypted1 + encrypted2;

  const auto decrypted = decrypt(encrypted, sk);
  const auto decoded = coder.decode(decrypted);

  EXPECT_NEAR(op, decoded, params.epsil);
}

TEST(EncryptedNums, testBalancedMult) {
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params = BalancedParams{.rw = 1.2, .epsil = 1e-8};
  Coder coder(params);
  // TODO parametrize
  double num1 = 109.8;
  double num2 = 9.02;

  const auto op = num1 * num2;

  const auto encoded1 = coder.encode(num1);
  const auto encoded2 = coder.encode(num2);
  const auto encrypted1 = encrypt(encoded1, pk);
  const auto encrypted2 = encrypt(encoded2, pk);

  const auto encrypted = encrypted1 * encrypted2;

  const auto decrypted = decrypt(encrypted, sk);
  const auto decoded = coder.decode(decrypted);

  EXPECT_NEAR(op, decoded, params.epsil * (num1 + num2));
}

TEST(EncryptedNums, testBalancedSlotsMult) {
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(15000L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params = BalancedSlotsParams{.rw = 1.2, .epsil = 1e-8};
  Coder coder(params);
  // TODO parametrize
  std::vector<double> nums1 = {0.0, 2.2, 109.8, 453.756};
  std::vector<double> nums2 = {1.0, 2.2, 9.02, 5.67};
  nums1.resize(sk.getContext().getNSlots());
  nums2.resize(sk.getContext().getNSlots());

  const auto op = nums1 * nums2;

  const auto encoded1 = coder.encode(nums1);
  const auto encoded2 = coder.encode(nums2);
  const auto encrypted1 = encrypt(encoded1, pk);
  const auto encrypted2 = encrypt(encoded2, pk);

  const auto encrypted = encrypted1 * encrypted2;

  const auto decrypted = decrypt(encrypted, sk);
  const auto decoded = coder.decode(decrypted);

  for (long i = 0; i < decoded.size(); ++i)
    EXPECT_NEAR(op[i], decoded[i], params.epsil * (nums1[i] + nums2[i]));
}

TEST(EncryptedNums, testBalancedSlotsAdd) {
  auto context =
      helib::ContextBuilder<helib::BGV>{}.p(47L).m(15000L).bits(50).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;
  //
  const auto params = BalancedSlotsParams{.rw = 1.2, .epsil = 1e-8};
  Coder coder(params);

  // TODO swapping last numbers around leads to wrong value
  std::vector<double> nums1 = {0.0, 2.2, 99.8, 45.05};
  std::vector<double> nums2 = {1.0, 2.2, 9.02, 53.76};
  nums1.resize(sk.getContext().getNSlots());
  nums2.resize(sk.getContext().getNSlots());

  const auto op = nums1 + nums2;

  const auto encoded1 = coder.encode(nums1);
  const auto encoded2 = coder.encode(nums2);
  const auto encrypted1 = encrypt(encoded1, pk);
  const auto encrypted2 = encrypt(encoded2, pk);

  const auto encrypted = encrypted1 + encrypted2;

  const auto decrypted = decrypt(encrypted, sk);
  const auto decoded = coder.decode(decrypted);

  for (long i = 0; i < decoded.size(); ++i)
    EXPECT_NEAR(op[i], decoded[i], params.epsil)
        << nums1[i] << " + " << nums2[i] << " = " << op[i];
}

// TODO sort out this table
// p                   m                   phi(m)
//  47                  4096                73734                24576 6 47
//  500                 15000                 4000                  8

INSTANTIATE_TEST_SUITE_P(
    variousSingleNumbers, FractionalEncryptedSingleNums,
    ::testing::Values(std::pair{
        Params<FractionalParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50),
            Coder{FractionalParams{
                .rw = 1.2, .epsil = 1e-8, .frac_degree = 4096}}},
        std::vector<double>{0.0, 546.0, 546.789, 23.456, 0.2345}}));

INSTANTIATE_TEST_SUITE_P(
    variousSingleNumbers, BalancedEncryptedSingleNums,
    ::testing::Values(std::pair{
        Params<BalancedParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50),
            Coder{BalancedParams{.rw = 1.2, .epsil = 1e-8}}},
        std::vector<double>{0.0, 546.0, 546.789, 23.456, 0.2345}}));

}  // namespace
