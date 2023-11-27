// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <helib/ArgMap.h>

#include <iostream>

#include "../balanced.h"
#include "../dual_poly.h"

using hekit::coder::BalancedEncodedPoly;
using hekit::coder::BalancedParams;
using hekit::coder::DualCoder;
using hekit::coder::DualPoly;
using hekit::coder::SparsePoly;

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
  const auto two_part =
      BalancedEncodedPoly{SparsePoly(std::map<long, long>{{0L, 2L}}), 0L};
  const auto two = DualPoly{two_part, two_part};

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
  long a = 1093;
  long b = 1097;
};

int main(int argc, char** argv) {
  Args args;
  std::string a_params_file;
  std::string b_params_file;

  double num = 0.2;
  double denom = 0.7;

  // clang-format off
  helib::ArgMap{}
      .arg("rw", args.rw)
      .arg("epsil", args.epsil)
      .arg("iterations", args.iterations)
      .arg("a", args.a)
      .arg("b", args.b)
      .arg("num", num)
      .arg("dem", denom)
      .parse(argc, argv);
  // clang-format on

  std::cout << "Effective p = " << args.a << " + " << args.b << " = "
            << args.a * args.b << std::endl;

  std::cout << "Initializing coder\n";
  //  Coder coder(BalancedSlotsParams{.rw = args.rw, .epsil = args.epsil});
  DualCoder coder(BalancedParams{.rw = args.rw, .epsil = args.epsil},
                  std::pair{args.a, args.b});

  std::cout << "Encoding and encrypting\n";
  //  const std::vector numerator_nums(a_crypto.nslots, 0.2);
  //  std::vector divisor_nums(a_crypto.nslots, 0.0);

  //  double step = -0.1;
  //  double tmp = 0;
  //  std::generate_n(divisor_nums.begin(), a_crypto.nslots,
  //                  [&tmp, &step]() mutable {
  //                    return tmp = 0.8 + step; /*tmp * tmp + 0.25;*/
  //                  });

  double numerator_nums = num;
  double divisor_nums = denom;

  const auto N = coder.encode(numerator_nums);
  const auto D = coder.encode(divisor_nums);

  for (long i = 0; i < args.iterations; ++i) {
    std::cout << "Performing division for iteration: " << i << std::endl;
    const auto [encoded_result, encoded_divisors] = goldschmidt(N, D, i);

    std::cout << "Decoding\n";
    // const std::vector decoded_results = coder.decode(decrypted_result);
    double decoded_results = coder.decode(encoded_result);

    //  const std::vector decoded_divisors = coder.decode(decrypted_divisors);
    double decoded_divisors = coder.decode(encoded_divisors);

    std::cout << "Printing results\n";
    //  for (long i = 0; i < decoded_results.size(); ++i) {
    //    std::cout << numerator_nums[i] << " / " << divisor_nums[i] << " = "
    //              << decoded_results[i] << " (D=" << decoded_divisors[i] <<
    //              ")\n";
    //  }

    std::cout << numerator_nums << " / " << divisor_nums << " = "
              << decoded_results << " (D=" << decoded_divisors << ")\n";
  }

  std::cout << "Fin." << std::endl;

  return 0;
}
