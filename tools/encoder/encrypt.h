// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <helib/helib.h>

#include <vector>

#include "balanced.h"
#include "fractional.h"

namespace hekit::coder {

inline NTL::ZZX SparsePolyToZZX(const SparsePoly& sparse_poly) {
  NTL::ZZX ntl_poly;
  for (const auto& [index, coeff] : sparse_poly) {
    NTL::SetCoeff(ntl_poly, index, coeff);
  }
  return ntl_poly;
}

inline SparsePoly ZZXToSparsePoly(const NTL::ZZX& ntl_poly) {
  SparsePoly sparse_poly;
  for (long i = 0; i < NTL::deg(ntl_poly) + 1; ++i) {
    const auto& coeff = ntl_poly[i];
    if (coeff != 0) sparse_poly[i] = NTL::conv<long>(coeff);
  }
  return sparse_poly;
}

// Correct to -p/2 to +p/2
void correctCoeffRange(NTL::ZZX& poly, long p) {
  for (long i = 0; i < NTL::deg(poly) + 1; ++i) {
    const auto& coeff = poly[i];
    if (coeff > p / 2) poly[i] = coeff - p;
  }
}

inline FractionalEncodedPoly<helib::Ctxt> encrypt(
    const FractionalEncodedPoly<SparsePoly>& encoded_poly,
    const helib::PubKey& pk) {
  const NTL::ZZX poly = SparsePolyToZZX(encoded_poly.poly());
  helib::Ctxt ctxt(pk);
  pk.Encrypt(ctxt, poly);
  return FractionalEncodedPoly{ctxt};
}

inline FractionalEncodedPoly<SparsePoly> decrypt(
    const FractionalEncodedPoly<helib::Ctxt>& encoded_poly,
    const helib::SecKey& sk) {
  const helib::Ctxt ctxt = encoded_poly.poly();
  NTL::ZZX poly;
  sk.Decrypt(poly, ctxt);
  correctCoeffRange(poly, sk.getContext().getP());
  return FractionalEncodedPoly{ZZXToSparsePoly(poly)};
}

inline BalancedEncodedPoly<helib::Ctxt> encrypt(
    const BalancedEncodedPoly<SparsePoly>& encoded_poly,
    const helib::PubKey& pk) {
  const NTL::ZZX poly = SparsePolyToZZX(encoded_poly.poly());
  helib::Ctxt ctxt(pk);
  pk.Encrypt(ctxt, poly);
  return BalancedEncodedPoly{ctxt, encoded_poly.digit()};
}

inline BalancedEncodedPoly<SparsePoly> decrypt(
    const BalancedEncodedPoly<helib::Ctxt>& encoded_poly,
    const helib::SecKey& sk) {
  const helib::Ctxt ctxt = encoded_poly.poly();
  NTL::ZZX poly;
  sk.Decrypt(poly, ctxt);
  correctCoeffRange(poly, sk.getContext().getP());
  return BalancedEncodedPoly{ZZXToSparsePoly(poly), encoded_poly.digit()};
}

inline BalancedSlotsEncodedPoly<helib::Ctxt> encrypt(
    const BalancedSlotsEncodedPoly<SparsePoly>& encoded_poly,
    const helib::PubKey& pk) {
  const auto poly = encoded_poly.poly().expand();
  const auto view = pk.getContext().getView();
  helib::Ctxt ctxt(pk);
  view.encrypt(ctxt, pk, poly);
  return BalancedSlotsEncodedPoly{ctxt, encoded_poly.digits()};
}

inline BalancedSlotsEncodedPoly<SparsePoly> decrypt(
    const BalancedSlotsEncodedPoly<helib::Ctxt>& encoded_poly,
    const helib::SecKey& sk) {
  const auto ctxt = encoded_poly.poly();
  std::vector<long> poly;
  const auto view = sk.getContext().getView();
  view.decrypt(ctxt, sk, poly);
  return BalancedSlotsEncodedPoly{SparsePoly{poly}, encoded_poly.digits()};
}

}  // namespace hekit::coder
