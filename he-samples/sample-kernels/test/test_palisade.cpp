// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>
#include <palisade.h>

#include <memory>
#include <vector>

namespace intel {
namespace he {
namespace palisade {

TEST(palisade, simple_real_numbers) {
  uint32_t multDepth = 1;
  uint32_t scaleFactorBits = 50;
  uint32_t batchSize = 8;

  lbcrypto::SecurityLevel securityLevel = lbcrypto::HEStd_128_classic;

  // The following call creates a CKKS crypto context based on the
  // arguments defined above.
  lbcrypto::CryptoContext<lbcrypto::DCRTPoly> cc =
      lbcrypto::CryptoContextFactory<lbcrypto::DCRTPoly>::genCryptoContextCKKS(
          multDepth, scaleFactorBits, batchSize, securityLevel);
  // Enable the features that you wish to use
  cc->Enable(ENCRYPTION);
  cc->Enable(SHE);

  auto keys = cc->KeyGen();
  cc->EvalMultKeyGen(keys.secretKey);
  cc->EvalAtIndexKeyGen(keys.secretKey, {1, -2});

  // Inputs
  std::vector<double> x1 = {0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 4.0, 5.0};
  std::vector<double> x2 = {5.0, 4.0, 3.0, 2.0, 1.0, 0.75, 0.5, 0.25};

  // Encoding as plaintexts
  lbcrypto::Plaintext ptxt1 = cc->MakeCKKSPackedPlaintext(x1);
  lbcrypto::Plaintext ptxt2 = cc->MakeCKKSPackedPlaintext(x2);

  // Encrypt the encoded vectors
  auto c1 = cc->Encrypt(keys.publicKey, ptxt1);
  auto c2 = cc->Encrypt(keys.publicKey, ptxt2);

  // Homomorphic addition
  auto cAdd = cc->EvalAdd(c1, c2);

  // Homomorphic subtraction
  auto cSub = cc->EvalSub(c1, c2);

  // Homomorphic scalar multiplication
  auto cScalar = cc->EvalMult(c1, 4.0);

  // Homomorphic multiplication
  auto cMul = cc->EvalMult(c1, c2);

  // Homomorphic rotations
  auto cRot1 = cc->EvalAtIndex(c1, 1);
  auto cRot2 = cc->EvalAtIndex(c1, -2);

  // Step 5: Decryption and output
  lbcrypto::Plaintext result;

  // Decrypt the result of addition
  cc->Decrypt(keys.secretKey, cAdd, &result);
  result->SetLength(batchSize);

  // Decrypt the result of subtraction
  cc->Decrypt(keys.secretKey, cSub, &result);
  result->SetLength(batchSize);

  // Decrypt the result of scalar multiplication
  cc->Decrypt(keys.secretKey, cScalar, &result);
  result->SetLength(batchSize);

  // Decrypt the result of multiplication
  cc->Decrypt(keys.secretKey, cMul, &result);
  result->SetLength(batchSize);

  // Decrypt the result of rotations
  cc->Decrypt(keys.secretKey, cRot1, &result);
  result->SetLength(batchSize);

  cc->Decrypt(keys.secretKey, cRot2, &result);
  result->SetLength(batchSize);

  ASSERT_TRUE(true);
}

}  // namespace palisade
}  // namespace he
}  // namespace intel
