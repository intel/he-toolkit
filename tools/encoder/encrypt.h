// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <helib/helib.h>

#include <algorithm>
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
    const BalancedSlotsEncodedPoly<SparseMultiPoly>& encoded_poly,
    const helib::PubKey& pk) {
  const std::vector polys = encoded_poly.poly().slots();
  std::vector<NTL::ZZX> ntl_polys;
  ntl_polys.reserve(pk.getContext().getNSlots());
  std::transform(polys.cbegin(), polys.cend(), std::back_inserter(ntl_polys),
                 SparsePolyToZZX);
  helib::Ctxt ctxt(pk);
  helib::PtxtArray ptxt(pk.getContext());
  ptxt.load(ntl_polys);
  ptxt.encrypt(ctxt);
  return BalancedSlotsEncodedPoly{ctxt, encoded_poly.digits()};
}

// HElib objects tend not to have out-of-place ops i.e. Ctxt
template <typename TXTL, typename TXTR>
inline auto operator*(const TXTL& lhs, const TXTR& rhs) {
  auto ans = lhs;
  ans *= rhs;
  return ans;
}

inline auto select(const helib::Ctxt& lpoly, const helib::Ctxt& rpoly,
                   const std::vector<long>& select_mask) {
  // Given a mask for the slots output selected poly and its complimentary poly
  std::vector<long> complimentary_mask = select_mask.size();
  std::for_each(complimentary_mask.begin(), complimentary_mask.end(),
                [](auto& bit) { bit = !bit; });

  const auto& context = lpoly.getContext();
  helib::PtxtArray selected_ptxt(context);
  helib::PtxtArray complimentary_ptxt(context);
  selected_ptxt.load(select_mask);
  selected_ptxt.load(complimentary_mask);

  auto selected = (lpoly * selected_ptxt) + (rpoly * complimentary_ptxt);
  auto complimentary = (lpoly * complimentary_ptxt) * (rpoly * selected_ptxt);
  return std::pair{selected, complimentary};
}

inline BalancedSlotsEncodedPoly<SparseMultiPoly> decrypt(
    const BalancedSlotsEncodedPoly<helib::Ctxt>& encoded_poly,
    const helib::SecKey& sk) {
  const helib::Ctxt ctxt = encoded_poly.poly();
  std::vector<NTL::ZZX> polys;
  helib::PtxtArray ptxt(sk.getContext());
  ptxt.decrypt(ctxt, sk);
  ptxt.store(polys);
  SparseMultiPoly sparse_multi_poly;
  sparse_multi_poly.slots().reserve(sk.getContext().getNSlots());
  std::transform(polys.cbegin(), polys.cend(),
                 std::back_inserter(sparse_multi_poly.slots()),
                 [p = sk.getContext().getP()](const auto& poly) {
                   auto new_poly = poly;
                   correctCoeffRange(new_poly, p);
                   return ZZXToSparsePoly(new_poly);
                 });
  return BalancedSlotsEncodedPoly{sparse_multi_poly, encoded_poly.digits()};
}

}  // namespace hekit::coder
