// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <iostream>

#include "../encrypt.h"

using hekit::coder::BalancedSlotsEncodedPoly;
using hekit::coder::BalancedSlotsParams;
using hekit::coder::Coder;
using hekit::coder::SparseMultiPoly;

template <typename EncodedPoly>
EncodedPoly goldschmidt(const EncodedPoly& N, const EncodedPoly& D,
                        long iterations) {
  // N/D Numerator and Divisor
  // F_i = 2 - D_i
  // N_i+1/D_i+1 = N_i/D_i * F_i/F_i

  if (iterations < 0)
    throw std::logic_error(
        "`goldschmidt` must be passed non-negative integers, not " +
        std::to_string(iterations));

  const auto* context_p = &N.poly().getContext();
  long nslots = context_p->getNSlots();
  const auto minus_one = BalancedSlotsEncodedPoly(
      helib::PtxtArray(*context_p, -1L), std::vector(0L, nslots));
  const auto minus_two = BalancedSlotsEncodedPoly(
      helib::PtxtArray(*context_p, -2L), std::vector(0L, nslots));

  for (long i = 0; i < iterations; ++i) {
    // F = 2 - D
    const auto F = (D + minus_two) * minus_one;
    N = N * F;
    D = D * F;
  }

  return N;
}

int main() {
  const helib::Context context =
      helib::ContextBuilder<helib::BGV>{}.p(47).m(20000).bits(500).build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;

  Coder coder(BalancedSlotsParams{.rw = 1.2, .epsil = 1e-8});

  const auto N = hekit::coder::encrypt(coder.encode({2.0, 2.0, 2.0}), pk);
  const auto D = hekit::coder::encrypt(coder.encode({2.0, 4.0, 6.0}), pk);
  const auto encrypted_result = goldschmidt(N, D, 1);
  const auto decrypted_result = hekit::coder::decrypt(encrypted_result, sk);
  const std::vector decoded_results = coder.decode(decrypted_result);

  for (const auto& result : decoded_results) {
    std::cout << result << '\n';
  }
  std::cout << std::endl;

  return 0;
}
