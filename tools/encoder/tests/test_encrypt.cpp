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

using Slots = std::vector<double>;

struct FractionalEncryptedSingleNums
    : public testing::TestWithParam<
          std::pair<Params<FractionalParams>, std::vector<double>>> {};
struct BalancedEncryptedSingleNums
    : public testing::TestWithParam<
          std::pair<Params<BalancedParams>, std::vector<double>>> {};
struct BalancedSlotsEncryptedSingleNums
    : public testing::TestWithParam<
          std::pair<Params<BalancedSlotsParams>, std::vector<Slots>>> {};

struct FractionalEncryptedTwoNums
    : public testing::TestWithParam<std::tuple<
          Params<FractionalParams>, std::vector<double>, std::vector<double>>> {
};
struct BalancedEncryptedTwoNums
    : public testing::TestWithParam<std::tuple<
          Params<BalancedParams>, std::vector<double>, std::vector<double>>> {};
struct BalancedSlotsEncryptedTwoNums
    : public testing::TestWithParam<
          std::tuple<Params<BalancedSlotsParams>, Slots, Slots>> {};

TEST(SparsePolyToZZX, testSparsePolyToZZXConversion) {
  auto original = SparsePoly({{1, 2}, {3, 4}});
  const auto decoded = ZZXToSparsePoly(SparsePolyToZZX(original));
  EXPECT_EQ(decoded, original);
}

template <typename EncodingSchemeParams, typename Data>
static inline void testEncryptDecrypt(const EncodingSchemeParams& get_params,
                                      const Data& input_nums) {
  const auto [bgv_cb, coder] = get_params;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  for (auto original : input_nums) {
    if constexpr (std::is_same_v<Data, std::vector<Slots>>)
      original.resize(crypto.context.getNSlots());

    const auto encoded = coder.encode(original);

    if constexpr (std::is_same_v<Data, std::vector<Slots>>) {
      const auto& inter_decode = coder.decode(encoded);
      for (long i = 0; i < original.size(); ++i)
        EXPECT_NEAR(original[i], inter_decode[i], params.epsil);
    } else {
      EXPECT_NEAR(original, coder.decode(encoded), params.epsil);
    }

    const auto encrypted = encrypt(encoded, crypto.pk);
    const auto decrypted = decrypt(encrypted, crypto.sk);

    EXPECT_EQ(encoded.poly(), decrypted.poly())
        << "Encoded Poly: " << encoded.poly().toString() << "\n"
        << "Decrypted Poly: " << decrypted.poly().toString() << "\n";

    const auto decoded = coder.decode(decrypted);

    if constexpr (std::is_same_v<Data, std::vector<Slots>>) {
      for (long i = 0; i < original.size(); ++i)
        EXPECT_NEAR(original[i], decoded[i], params.epsil);
    } else {
      EXPECT_NEAR(original, decoded, params.epsil);
    }
  }
}

TEST_P(FractionalEncryptedSingleNums, DISABLED_testEncryptDecrypt) {
  const auto [params, input_nums] = GetParam();
  testEncryptDecrypt(params, input_nums);
}

TEST_P(BalancedEncryptedSingleNums, testEncryptDecrypt) {
  const auto [params, input_nums] = GetParam();
  testEncryptDecrypt(params, input_nums);
}

TEST_P(BalancedSlotsEncryptedSingleNums, testEncryptDecrypt) {
  const auto [params, input_nums] = GetParam();
  testEncryptDecrypt(params, input_nums);
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

TEST_P(FractionalEncryptedTwoNums, testAdd) {
  const auto [test_config, nums1, nums2] = GetParam();
  const auto [bgv_cb, coder] = test_config;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  ASSERT_EQ(nums1.size(), nums2.size());

  for (long i = 0; i < nums1.size(); ++i) {
    const auto& num1 = nums1[i];
    const auto& num2 = nums2[i];

    const auto expected = num1 + num2;

    const auto encoded1 = coder.encode(num1);
    const auto encoded2 = coder.encode(num2);
    const auto encrypted1 = encrypt(encoded1, crypto.pk);
    const auto encrypted2 = encrypt(encoded2, crypto.pk);

    const auto encrypted = encrypted1 + encrypted2;

    const auto decrypted = decrypt(encrypted, crypto.sk);
    const auto decoded = coder.decode(decrypted);

    EXPECT_NEAR(expected, decoded, 2 * params.epsil)
        << num1 << " + " << num2 << " = " << expected;
  }
}

TEST_P(FractionalEncryptedTwoNums, DISABLED_testMult) {
  const auto [test_config, nums1, nums2] = GetParam();
  const auto [bgv_cb, coder] = test_config;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  ASSERT_EQ(nums1.size(), nums2.size());

  for (long i = 0; i < nums1.size(); ++i) {
    const auto& num1 = nums1[i];
    const auto& num2 = nums2[i];

    const auto expected = num1 * num2;

    const auto encoded1 = coder.encode(num1);
    const auto encoded2 = coder.encode(num2);
    const auto encrypted1 = encrypt(encoded1, crypto.pk);
    const auto encrypted2 = encrypt(encoded2, crypto.pk);

    const auto encrypted = encrypted1 * encrypted2;

    std::cerr << "decrypted1: "
              << decrypt(encrypted1, crypto.sk).poly().toString() << std::endl;
    std::cerr << "decrypted2: "
              << decrypt(encrypted2, crypto.sk).poly().toString() << std::endl;
    const auto decrypted = decrypt(encrypted, crypto.sk);
    std::cerr << "decrypted poly: " << decrypted.poly().toString() << std::endl;
    const auto decoded = coder.decode(decrypted);

    EXPECT_NEAR(expected, decoded, params.epsil * (num1 + num2))
        << num1 << " * " << num2 << " = " << expected;
  }
}

TEST_P(BalancedEncryptedTwoNums, testAdd) {
  const auto [test_config, nums1, nums2] = GetParam();
  const auto [bgv_cb, coder] = test_config;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  ASSERT_EQ(nums1.size(), nums2.size());

  for (long i = 0; i < nums1.size(); ++i) {
    const auto& num1 = nums1[i];
    const auto& num2 = nums2[i];

    const auto expected = num1 + num2;

    const auto encoded1 = coder.encode(num1);
    const auto encoded2 = coder.encode(num2);
    const auto encrypted1 = encrypt(encoded1, crypto.pk);
    const auto encrypted2 = encrypt(encoded2, crypto.pk);

    const auto encrypted = encrypted1 + encrypted2;

    const auto decrypted = decrypt(encrypted, crypto.sk);
    const auto decoded = coder.decode(decrypted);

    EXPECT_NEAR(expected, decoded, 2 * params.epsil)
        << num1 << " + " << num2 << " = " << expected;
  }
}

TEST_P(BalancedEncryptedTwoNums, testMult) {
  const auto [test_config, nums1, nums2] = GetParam();
  const auto [bgv_cb, coder] = test_config;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  ASSERT_EQ(nums1.size(), nums2.size());

  for (long i = 0; i < nums1.size(); ++i) {
    const auto& num1 = nums1[i];
    const auto& num2 = nums2[i];

    const auto expected = num1 * num2;

    const auto encoded1 = coder.encode(num1);
    const auto encoded2 = coder.encode(num2);
    const auto encrypted1 = encrypt(encoded1, crypto.pk);
    const auto encrypted2 = encrypt(encoded2, crypto.pk);

    const auto encrypted = encrypted1 * encrypted2;

    const auto decrypted = decrypt(encrypted, crypto.sk);
    const auto decoded = coder.decode(decrypted);

    EXPECT_NEAR(expected, decoded, params.epsil * (num1 + num2))
        << num1 << " * " << num2 << " = " << expected;
  }
}

TEST_P(BalancedSlotsEncryptedTwoNums, testMult) {
  auto [test_config, nums1, nums2] = GetParam();
  const auto [bgv_cb, coder] = test_config;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  ASSERT_EQ(nums1.size(), nums2.size());

  nums1.resize(crypto.context.getNSlots());
  nums2.resize(crypto.context.getNSlots());

  const auto op = nums1 * nums2;

  const auto encoded1 = coder.encode(nums1);
  const auto encoded2 = coder.encode(nums2);
  const auto encrypted1 = encrypt(encoded1, crypto.pk);
  const auto encrypted2 = encrypt(encoded2, crypto.pk);

  const auto encrypted = encrypted1 * encrypted2;

  const auto decrypted = decrypt(encrypted, crypto.sk);
  const auto decoded = coder.decode(decrypted);

  for (long i = 0; i < decoded.size(); ++i)
    EXPECT_NEAR(op[i], decoded[i], params.epsil * (nums1[i] + nums2[i]));
}

TEST_P(BalancedSlotsEncryptedTwoNums, testMultWithPtxtArray) {
  auto [test_config, nums1, nums2] = GetParam();
  const auto [bgv_cb, coder] = test_config;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  ASSERT_EQ(nums1.size(), nums2.size());

  nums1.resize(crypto.context.getNSlots());
  nums2.resize(crypto.context.getNSlots());

  const auto op = nums1 * nums2;

  const auto encoded1 = coder.encode(nums1);
  const auto encoded2 = coder.encode(nums2);
  const auto encrypted1 = encrypt(encoded1, crypto.pk);
  const auto ptxt2 = hekit::coder::BalancedSlotsEncodedPoly{
      SparseMultiPolyToPtxtArray(encoded2.poly(), crypto.context),
      encoded2.digits()};

  const auto encrypted = encrypted1 * ptxt2;

  // const auto decrypted = decrypt(encrypted, crypto.sk);
  // const auto decoded = coder.decode(decrypted);

  // for (long i = 0; i < decoded.size(); ++i)
  //   EXPECT_NEAR(op[i], decoded[i], params.epsil * (nums1[i] + nums2[i]));
}

TEST_P(BalancedSlotsEncryptedTwoNums, testAdd) {
  auto [test_config, nums1, nums2] = GetParam();
  const auto [bgv_cb, coder] = test_config;
  Crypto crypto(bgv_cb);
  auto params = coder.params();

  ASSERT_EQ(nums1.size(), nums2.size());

  nums1.resize(crypto.context.getNSlots());
  nums2.resize(crypto.context.getNSlots());

  const auto op = nums1 + nums2;

  const auto encoded1 = coder.encode(nums1);
  const auto encoded2 = coder.encode(nums2);
  const auto encrypted1 = encrypt(encoded1, crypto.pk);
  const auto encrypted2 = encrypt(encoded2, crypto.pk);

  const auto encrypted = encrypted1 + encrypted2;

  const auto decrypted = decrypt(encrypted, crypto.sk);
  const auto decoded = coder.decode(decrypted);

  for (long i = 0; i < decoded.size(); ++i)
    EXPECT_NEAR(op[i], decoded[i], params.epsil * 2)
        << nums1[i] << " + " << nums2[i] << std::endl;
}

INSTANTIATE_TEST_SUITE_P(
    variousSingleNumbers, FractionalEncryptedSingleNums,
    ::testing::Values(std::pair{
        Params<FractionalParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50),
            Coder{FractionalParams{
                .rw = 1.2, .epsil = 1e-8, .frac_degree = 8192}}},
        std::vector<double>{0.0, 546.0, 546.789, 23.456, 0.2345}}));

INSTANTIATE_TEST_SUITE_P(
    variousTwoNumbers, FractionalEncryptedTwoNums,
    ::testing::Values(std::tuple{
        Params<FractionalParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50),
            //         127                   8                  43520 16384 2048
            //            helib::ContextBuilder<helib::BGV>{}.p(127).m(43520).bits(50),
            Coder{FractionalParams{
                .rw = 1.2, .epsil = 1e-8, .frac_degree = 4096}}},
        //        std::vector<double>{0.0, 1.0, 5.0, 5.789, 2.4, 0.23, 1.8},
        std::vector<double>{0.1},
        //        std::vector<double>{0.0, 1.1, 6.0, 6.281, 5.0, 0.45, 9.2}}));
        std::vector<double>{0.5}}));

INSTANTIATE_TEST_SUITE_P(
    variousSingleNumbers, BalancedEncryptedSingleNums,
    ::testing::Values(std::pair{
        Params<BalancedParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50),
            Coder{BalancedParams{.rw = 1.2, .epsil = 1e-8}}},
        std::vector<double>{0.0, 546.0, 546.789, 23.456, 0.2345}}));

INSTANTIATE_TEST_SUITE_P(
    variousTwoNumbers, BalancedEncryptedTwoNums,
    ::testing::Values(std::tuple{
        Params<BalancedParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50),
            Coder{BalancedParams{.rw = 1.2, .epsil = 1e-8}}},
        std::vector<double>{0.0, 1.0, 5.0, 5.789, 2.4, 0.23, 1.8},
        std::vector<double>{0.0, 1.1, 6.0, 6.281, 5.0, 0.45, 9.2}}));

INSTANTIATE_TEST_SUITE_P(
    variousSingleNumbers, BalancedSlotsEncryptedSingleNums,
    ::testing::Values(std::pair{
        Params<BalancedSlotsParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(15000L).bits(50),
            Coder{BalancedSlotsParams{.rw = 1.2, .epsil = 1e-8}}},
        std::vector<Slots>{{0.0, 2.2, 109.8, 453.756}}}));

// p     d      m        phi_m    slots
// 47    500    20000    8000     16

INSTANTIATE_TEST_SUITE_P(
    variousTwoNumbers, BalancedSlotsEncryptedTwoNums,
    ::testing::Values(std::tuple{
        Params<BalancedSlotsParams>{
            helib::ContextBuilder<helib::BGV>{}.p(47L).m(20000L).bits(50),
            Coder{BalancedSlotsParams{.rw = 1.2, .epsil = 1e-8}}},
        Slots{0.0, 1.0, 5.0, 5.789, 2.4, 0.23, 1.8},
        Slots{0.0, 1.1, 6.0, 6.281, 5.0, 0.45, 9.2}}));

}  // namespace
