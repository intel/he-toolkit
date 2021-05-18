// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <palisade.h>

#include <functional>
#include <iostream>
#include <memory>
#include <numeric>
#include <utility>
#include <vector>

#pragma once

namespace intel {
namespace he {
namespace palisade {

inline auto generatePalisadeCKKSContext(int poly_modulus_degree,
                                        std::vector<int> coeff_modulus_bits) {
  uint64_t numPrimes =
      coeff_modulus_bits.size();  // count of primes for moduli chain
  uint64_t scaleExp = 50;         // plaintext scaling factor

  // bits in the base of digits in key-switching/relinearization
  uint64_t relinWindow = 0;                  // 0 = RNS Decomposition
  int batch_size = poly_modulus_degree / 2;  // Batch size == slot count
  int depth = 1;  // Starting Depth of supported computation circuit? (unused?)
  int maxDepth = 5;       // Max power of secret key for relin key generation
  int firstModSize = 60;  // bit-length of the first modulus
  uint32_t numLargeDigits = 4;  // number of big digits when ksTech == Hybrid

  // Get CKKS crypto context and generate encryption keys.
  auto palisade_context = lbcrypto::CryptoContextFactory<lbcrypto::DCRTPoly>::
      genCryptoContextCKKSWithParamsGen(
          poly_modulus_degree * 2, numPrimes, scaleExp, relinWindow, batch_size,
          MODE::OPTIMIZED, depth, maxDepth, firstModSize,
          lbcrypto::KeySwitchTechnique::BV,
          lbcrypto::RescalingTechnique::APPROXRESCALE, numLargeDigits);

  palisade_context->Enable(PKESchemeFeature::ENCRYPTION);
  palisade_context->Enable(PKESchemeFeature::SHE);
  palisade_context->Enable(PKESchemeFeature::LEVELEDSHE);

  return palisade_context;
}

inline auto generatePalisadeBFVContext(int poly_modulus_degree,
                                       std::vector<int> coeff_modulus_bits) {
  int plaintext_modulus = 65537;
  lbcrypto::SecurityLevel security_level = lbcrypto::HEStd_NotSet;
  float dist = 3.19;
  int num_adds = 0;
  int num_mults = coeff_modulus_bits.size();
  int num_key_switches = 0;
  MODE mode = OPTIMIZED;
  // max size of relin key. 2 means we relin after every mult
  int max_depth = 2;

  // bits in the base of digits in key-switching/relinearization
  // (0 - means to use only CRT decomposition)
  uint64_t relin_window = 0;
  int dcrt_bits = 60;  // size of "small" CRT moduli.

  auto palisade_context = lbcrypto::CryptoContextFactory<lbcrypto::DCRTPoly>::
      genCryptoContextBFVrns(plaintext_modulus, security_level, dist, num_adds,
                             num_mults, num_key_switches, mode, max_depth,
                             relin_window, dcrt_bits, poly_modulus_degree);

  palisade_context->Enable(PKESchemeFeature::ENCRYPTION);
  palisade_context->Enable(PKESchemeFeature::SHE);

  return palisade_context;
}

inline auto generatePalisadeBFVBContext(int poly_modulus_degree,
                                        std::vector<int> coeff_modulus_bits) {
  int plaintext_modulus = 65537;
  lbcrypto::SecurityLevel security_level = lbcrypto::HEStd_NotSet;
  float dist = 3.19;
  int num_adds = 0;
  int num_mults = coeff_modulus_bits.size();
  int num_key_switches = 0;
  MODE mode = OPTIMIZED;
  // max size of relin key. 2 means we relin after every mult
  int max_depth = 2;

  // bits in the base of digits in key-switching/relinearization
  // (0 - means to use only CRT decomposition)
  uint64_t relin_window = 0;
  int dcrt_bits = 60;  // size of "small" CRT moduli.

  auto palisade_context = lbcrypto::CryptoContextFactory<lbcrypto::DCRTPoly>::
      genCryptoContextBFVrnsB(plaintext_modulus, security_level, dist, num_adds,
                              num_mults, num_key_switches, mode, max_depth,
                              relin_window, dcrt_bits, poly_modulus_degree);

  palisade_context->Enable(PKESchemeFeature::ENCRYPTION);
  palisade_context->Enable(PKESchemeFeature::SHE);

  return palisade_context;
}

}  // namespace palisade
}  // namespace he
}  // namespace intel
