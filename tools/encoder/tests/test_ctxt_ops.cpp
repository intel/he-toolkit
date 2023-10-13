// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include "../ctxt_ops.h"

using hekit::coder::operator*;

namespace {

// Move out as a commonality?
struct Crypto {
  Crypto() = delete;
  explicit Crypto(const helib::ContextBuilder<helib::BGV>& cb)
      : context(cb.build()), sk(context), pk((sk.GenSecKey(), sk)) {}

  helib::Context context;
  helib::SecKey sk;
  const helib::PubKey& pk;
};

TEST(tmp, DISABLED_checkSimpleMasking) {
  Crypto crypto{helib::ContextBuilder<helib::BGV>{}.p(47L).m(20000L).bits(50)};

  helib::PtxtArray ptxt(crypto.context);
  ptxt.load(std::vector{2L, 4L, 6L, 8L});
  helib::Ctxt ctxt(crypto.pk);
  ptxt.encrypt(ctxt);

  helib::PtxtArray mask(crypto.context);
  mask.load(std::vector{1L, 0L, 1L, 0L});

  // const auto ans = hekit::coder::operator*(ctxt, mask);
  const auto ans = ctxt * mask;

  helib::PtxtArray decrypted(crypto.context);
  decrypted.decrypt(ans, crypto.sk);

  std::vector<NTL::ZZX> slots;
  decrypted.store(slots);

  for (const auto& slot : slots) std::cerr << slot << std::endl;
}

TEST(tmp, DISABLED_checkSelect) {
  Crypto crypto{helib::ContextBuilder<helib::BGV>{}.p(47L).m(20000L).bits(50)};

  helib::PtxtArray lpoly_ptxt(crypto.context);
  lpoly_ptxt.load(std::vector{2L, 4L});
  helib::Ctxt lpoly(crypto.pk);
  lpoly_ptxt.encrypt(lpoly);

  helib::PtxtArray rpoly_ptxt(crypto.context);
  rpoly_ptxt.load(std::vector{3L, 5L});
  helib::Ctxt rpoly(crypto.pk);
  rpoly_ptxt.encrypt(rpoly);

  const auto [selected, complimentary] =
      hekit::coder::select(lpoly, rpoly, std::vector<long>{0, 1});

  helib::PtxtArray selected_ptxt(crypto.context);
  selected_ptxt.decrypt(selected, crypto.sk);

  helib::PtxtArray complimentary_ptxt(crypto.context);
  complimentary_ptxt.decrypt(complimentary, crypto.sk);

  std::vector<NTL::ZZX> selected_slots;
  selected_ptxt.store(selected_slots);

  for (const auto& slot : selected_slots) std::cerr << slot << std::endl;

  std::vector<NTL::ZZX> complimentary_slots;
  complimentary_ptxt.store(complimentary_slots);

  for (const auto& slot : complimentary_slots)
    std::cerr << "  " << slot << std::endl;
}

TEST(tmp, DISABLED_checkShiftSlots) {
  Crypto crypto{helib::ContextBuilder<helib::BGV>{}.p(47L).m(20000L).bits(50)};
  helib::Ctxt ctxt(crypto.pk);
  NTL::ZZX first, second;
  SetCoeff(first, 0, 2);
  SetCoeff(second, 1, 1);
  helib::PtxtArray nums(crypto.context);
  nums.load(std::vector{first, second});
  nums.encrypt(ctxt);

  auto ans = hekit::coder::shift(ctxt, std::vector{1L, 2L});
  helib::PtxtArray decrypted_ptxt(crypto.context);
  decrypted_ptxt.decrypt(ans, crypto.sk);
  std::vector<NTL::ZZX> decrypt;
  decrypted_ptxt.store(decrypt);

  std::cerr << first << std::endl;
  std::cerr << decrypt[0] << std::endl;
  std::cerr << second << std::endl;
  std::cerr << decrypt[1] << std::endl;
}

TEST(tmp, DISABLED_checkShift) {
  Crypto crypto{helib::ContextBuilder<helib::BGV>{}.p(47L).m(32640L).bits(50)};
  helib::Ctxt ctxt(crypto.pk);
  NTL::ZZX ptxt;
  SetCoeff(ptxt, 5, 2);
  std::cerr << ptxt << std::endl;

  crypto.pk.Encrypt(ctxt, ptxt);
  ctxt = hekit::coder::shift(ctxt, 1);
  NTL::ZZX decrypted;
  crypto.sk.Decrypt(decrypted, ctxt);
  std::cerr << decrypted << std::endl;
}

}  // namespace
