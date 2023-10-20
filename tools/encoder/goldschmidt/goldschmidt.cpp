// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <helib/ArgMap.h>

#include <iostream>

#include "../encrypt.h"

using hekit::coder::BalancedSlotsEncodedPoly;
using hekit::coder::BalancedSlotsParams;
using hekit::coder::Coder;
using hekit::coder::SparseMultiPoly;

template <typename EncodedPoly>
auto goldschmidt(const EncodedPoly& numerator, const EncodedPoly& denominator,
                 long iterations) {
  // N/D Numerator and Divisor
  // F_i = 2 - D_i
  // N_i+1/D_i+1 = N_i/D_i * F_i/F_i

  if (iterations < 0)
    throw std::logic_error(
        "`goldschmidt` must be passed non-negative integers, not " +
        std::to_string(iterations));

  auto N = numerator;
  auto D = denominator;
  const auto* context_p = &N.poly().getContext();
  long nslots = context_p->getNSlots();
  // TODO negation op make this obsolete
  const auto minus_one = BalancedSlotsEncodedPoly(
      helib::PtxtArray(*context_p, -1L), std::vector(nslots, 0L));
  const auto two = BalancedSlotsEncodedPoly(helib::PtxtArray(*context_p, 2L),
                                            std::vector(nslots, 0L));

  for (long i = 0; i < iterations; ++i) {
    // F = 2 - D
    const auto F = D * minus_one + two;
    N = N * F;
    D = D * F;
  }

  return std::pair{N, D};
}

struct Args {
  double rw = 1.2;
  double epsil = 1e-8;
  long iterations = 5;
  // read in via file
  long p;
  long m;
  long bits;
};

int main(int argc, char** argv) {
  Args args;
  std::string params_file;

  // clang-format off
  helib::ArgMap{}
      .arg("rw", args.rw)
      .arg("epsil", args.epsil)
      .arg("iterations", args.iterations)
      .required()
      .positional()
      .arg("params", params_file)
      .parse(argc, argv);

  helib::ArgMap{}
      .arg("p", args.p)
      .arg("m", args.m)
      .arg("bits", args.bits)
      .parse(params_file);
  // clang-format on

  std::cout << "Initializing HElib Context and keys\n";
  const helib::Context context = helib::ContextBuilder<helib::BGV>{}
                                     .p(args.p)
                                     .m(args.m)
                                     .bits(args.bits)
                                     .build();
  helib::SecKey sk(context);
  sk.GenSecKey();
  const helib::PubKey& pk = sk;

  std::cout << "Initializing coder\n";
  Coder coder(BalancedSlotsParams{.rw = args.rw, .epsil = args.epsil});

  std::cout << "Encoding and encrypting\n";
  const std::vector numerator_nums(context.getNSlots(), 0.2);
  std::vector divisor_nums(context.getNSlots(), 0.0);

  double tmp = 0.2;
  std::generate_n(divisor_nums.begin(), context.getNSlots(), [&tmp]() mutable {
    return tmp = 1.2; /*tmp * tmp + 0.25;*/
  });
  const auto N = hekit::coder::encrypt(coder.encode(numerator_nums), pk);
  const auto D = hekit::coder::encrypt(coder.encode(divisor_nums), pk);

  std::cout << "Performing division\n";
  const auto [encrypted_result, encrypted_divisors] =
      goldschmidt(N, D, args.iterations);

  std::cout << "Decrypting and decoding\n";
  const auto decrypted_result = hekit::coder::decrypt(encrypted_result, sk);
  const std::vector decoded_results = coder.decode(decrypted_result);

  const auto decrypted_divisors = hekit::coder::decrypt(encrypted_divisors, sk);
  const std::vector decoded_divisors = coder.decode(decrypted_divisors);

  std::cout << "Printing results\n";
  for (long i = 0; i < decoded_results.size(); ++i) {
    std::cout << numerator_nums[i] << " / " << divisor_nums[i] << " = "
              << decoded_results[i] << " (D=" << decoded_divisors[i] << ")\n";
  }
  std::cout << "Fin." << std::endl;

  return 0;
}
