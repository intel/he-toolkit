// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <helib/ArgMap.h>

#include <iostream>

#include "../encrypt.h"

using hekit::coder::BalancedParams;
using hekit::coder::BalancedSlotsEncodedPoly;
using hekit::coder::BalancedSlotsParams;
using hekit::coder::Coder;
using hekit::coder::DualCoder;
using hekit::coder::DualPoly;
using hekit::coder::SparseMultiPoly;

template <template <typename> typename EncodedPoly, typename Poly>
auto setTwo(const DualPoly<EncodedPoly<Poly>>& N,
            const DualPoly<EncodedPoly<Poly>>& D) {
  const auto& numerator_context = N.polys().first.poly().getContext();
  const auto& denominator_context = N.polys().second.poly().getContext();
  long nslots = numerator_context.getNSlots();

  if constexpr (std::is_same_v<EncodedPoly<Poly>,
                               BalancedSlotsEncodedPoly<Poly>>) {
    return DualPoly{EncodedPoly{helib::PtxtArray(numerator_context, 2L),
                                std::vector(nslots, 0L)},
                    EncodedPoly{helib::PtxtArray(denominator_context, 2L),
                                std::vector(nslots, 0L)}};
  } else {
    auto first = NTL::ZZX{};
    SetCoeff(first, 0, 2);
    auto second = NTL::ZZX{};
    SetCoeff(second, 0, 2);
    //    std::cout << first << "\n" << second << std::endl;
    // Unlike PtxtArray no limit defined by context
    return DualPoly{EncodedPoly{first, 0L}, EncodedPoly{second, 0L}};
  }
}

template <template <typename> typename EncodedPoly, typename Poly>
inline auto setTwo(const EncodedPoly<Poly>& N, const EncodedPoly<Poly>& D) {
  const auto& numerator_context = N.polys().first.poly().getContext();
  const auto& denominator_context = N.polys().second.poly().getContext();
  long nslots = numerator_context.getNSlots();

  if constexpr (std::is_same_v<EncodedPoly<Poly>,
                               BalancedSlotsEncodedPoly<Poly>>) {
    return EncodedPoly{helib::PtxtArray(numerator_context, 2L),
                       std::vector(nslots, 0L)};
  } else {
    return EncodedPoly{helib::PtxtArray(numerator_context, 2L), 0L};
  }
}

template <typename EncodedPoly>
auto goldschmidt(const EncodedPoly& numerator, const EncodedPoly& denominator,
                 long iterations) {
  if (iterations < 0)
    throw std::logic_error(
        "`goldschmidt` must be passed non-negative integers for iterations, "
        "not " +
        std::to_string(iterations));

  auto N = numerator;
  auto D = denominator;
  const auto two = setTwo(N, D);

  // N/D Numerator and Divisor
  // F_i = 2 - D_i
  // N_i+1/D_i+1 = N_i/D_i * F_i/F_i
  for (long i = 0; i < iterations; ++i) {
    const auto F = -D + two;
    N = N * F;
    D = D * F;
  }

  return std::pair{N, D};
}

struct Args {
  // read in via cli
  double rw = 1.2;
  double epsil = 1e-8;
  long iterations = 5;
  // read in via file
  long a_p;
  long a_m;
  long a_bits;
  long b_p;
  long b_m;
  long b_bits;
};

struct Crypto {
  Crypto() = delete;
  explicit Crypto(long p, long m, long bits)
      : context(
            helib::ContextBuilder<helib::BGV>{}.p(p).m(m).bits(bits).build()),
        sk(context),
        pk((sk.GenSecKey(), sk)),
        p(p),
        nslots(context.getNSlots()) {}

  helib::Context context;
  helib::SecKey sk;
  const helib::PubKey& pk;
  long p;
  long nslots;
};

int main(int argc, char** argv) {
  Args args;
  std::string a_params_file;
  std::string b_params_file;

  // clang-format off
  helib::ArgMap{}
      .arg("rw", args.rw)
      .arg("epsil", args.epsil)
      .arg("iterations", args.iterations)
      .required()
      .positional()
      .arg("a_params", a_params_file)
      .arg("b_params", b_params_file)
      .parse(argc, argv);

  helib::ArgMap{}
      .arg("p", args.a_p)
      .arg("m", args.a_m)
      .arg("bits", args.a_bits)
      .parse(a_params_file);

  helib::ArgMap{}
      .arg("p", args.b_p)
      .arg("m", args.b_m)
      .arg("bits", args.b_bits)
      .parse(b_params_file);
  // clang-format on

  std::cout << "Initializing HElib Context and keys\n";
  const Crypto a_crypto(args.a_p, args.a_m, args.a_bits);
  const Crypto b_crypto(args.b_p, args.b_m, args.b_bits);

  std::cout << "Initializing coder\n";
  //  Coder coder(BalancedSlotsParams{.rw = args.rw, .epsil = args.epsil});
  DualCoder coder(BalancedParams{.rw = args.rw, .epsil = args.epsil},
                  std::pair{a_crypto.p, b_crypto.p});

  std::cout << "Encoding and encrypting\n";
  //  const std::vector numerator_nums(a_crypto.nslots, 0.2);
  //  std::vector divisor_nums(a_crypto.nslots, 0.0);

  //  double step = -0.1;
  //  double tmp = 0;
  //  std::generate_n(divisor_nums.begin(), a_crypto.nslots,
  //                  [&tmp, &step]() mutable {
  //                    return tmp = 0.8 + step; /*tmp * tmp + 0.25;*/
  //                  });

  double numerator_nums = 0.2;
  double divisor_nums = 0.7;

  std::pair pks{a_crypto.pk, b_crypto.pk};
  std::pair sks{a_crypto.sk, b_crypto.sk};
  const auto N = hekit::coder::encrypt(coder.encode(numerator_nums), pks);
  const auto D = hekit::coder::encrypt(coder.encode(divisor_nums), pks);

  for (long i = 0; i < args.iterations; ++i) {
    std::cout << "Performing division for iteration: " << i << std::endl;
    const auto [encrypted_result, encrypted_divisors] = goldschmidt(N, D, i);

    std::cout << "Decrypting and decoding\n";
    const auto decrypted_result = hekit::coder::decrypt(encrypted_result, sks);
    // const std::vector decoded_results = coder.decode(decrypted_result);
    double decoded_results = coder.decode(decrypted_result);

    const auto decrypted_divisors =
        hekit::coder::decrypt(encrypted_divisors, sks);
    //  const std::vector decoded_divisors = coder.decode(decrypted_divisors);
    double decoded_divisors = coder.decode(decrypted_divisors);

    std::cout << "Printing results\n";
    //  for (long i = 0; i < decoded_results.size(); ++i) {
    //    std::cout << numerator_nums[i] << " / " << divisor_nums[i] << " = "
    //              << decoded_results[i] << " (D=" << decoded_divisors[i] <<
    //              ")\n";
    //  }

    std::cout << numerator_nums << " / " << divisor_nums << " = "
              << decoded_results << " (D=" << decoded_divisors << ")\n";

    std::cout << "Degree divisors: "
              << decrypted_divisors.polys().first.poly().degree() << std::endl;
    std::cout << "Degree results: "
              << decrypted_result.polys().first.poly().degree() << std::endl;
  }

  std::cout << "Fin." << std::endl;

  return 0;
}
