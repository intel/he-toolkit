// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <helib/ArgMap.h>

#include <functional>
#include <iostream>
#include <numeric>
#include <string>

#include "../balanced.h"
#include "../npoly.h"

using hekit::coder::BalancedEncodedPoly;
using hekit::coder::BalancedParams;
using hekit::coder::NCoder;
using hekit::coder::NPoly;
using hekit::coder::SparsePoly;

template <typename EncodedPoly, typename T>
auto goldschmidt(const EncodedPoly& numerator, const EncodedPoly& denominator,
                 long iterations, const NCoder<T>& coder) {
  if (iterations < 0)
    throw std::logic_error(
        "`goldschmidt` must be passed non-negative integers for iterations, "
        "not " +
        std::to_string(iterations));

  auto N = numerator;
  auto D = denominator;
  //  const auto two_part = std::vector(N.size(),
  //    BalancedEncodedPoly{SparsePoly(std::map<long, long>{{0L, 2L}}), 0L});
  //  const auto two = NPoly{two_part};
  const auto two = coder.encode(2.0);

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
  std::string mods = "1093,1097";
};

auto stringToMods(const std::string& mods_str) {
  std::istringstream iss(mods_str);
  std::vector<long> mods;
  std::string s;
  while (std::getline(iss, s, ',')) {
    mods.push_back(std::stol(s));
  }
  return mods;
}

int main(int argc, char** argv) {
  Args args;

  double num = 0.2;
  double denom = 0.7;

  // clang-format off
  helib::ArgMap{}
      .arg("rw", args.rw)
      .arg("epsil", args.epsil)
      .arg("iterations", args.iterations)
      .arg("mods", args.mods)
      .arg("num", num)
      .arg("den", denom)
      .parse(argc, argv);
  // clang-format on

  std::vector mods = stringToMods(args.mods);
  std::cout << "Effective p = ";
  for (const auto& mod : mods) std::cout << mod << " + ";
  std::cout << " = "
            << std::accumulate(mods.cbegin(), mods.cend(), 1L,
                               std::multiplies<long>{})
            << std::endl;

  std::cout << "Initializing coder\n";
  //  Coder coder(BalancedSlotsParams{.rw = args.rw, .epsil = args.epsil});
  NCoder coder(BalancedParams{.rw = args.rw, .epsil = args.epsil}, mods);

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
    const auto [encoded_result, encoded_divisors] = goldschmidt(N, D, i, coder);

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
              << numerator_nums / divisor_nums << std::endl;
    std::cout << coder.decode(N) << " / " << coder.decode(D) << " = "
              << decoded_results << " (D=" << decoded_divisors << ")\n";
  }

  std::cout << "Fin." << std::endl;

  return 0;
}
