// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <helib/helib.h>

#include <vector>

#include "balanced.h"
#include "fractional.h"

namespace hekit::coder {

FractionalEncodedPoly<helib::Ctxt> encrypt(
    const FractionalEncodedPoly<SparsePoly>& encoded_poly,
    const helib::PubKey& pk) {
  const auto poly = encoded_poly.poly().expand();
  const auto view = pk.getContext().getView();
  helib::Ctxt ctxt(pk);
  view.encrypt(ctxt, pk, poly);
  return FractionalEncodedPoly{ctxt};
}

FractionalEncodedPoly<SparsePoly> encrypt(
    const FractionalEncodedPoly<helib::Ctxt>& encoded_poly,
    const helib::SecKey& sk) {
  const auto ctxt = encoded_poly.poly();
  std::vector<long> poly;
  const auto view = sk.getContext().getView();
  view.decrypt(ctxt, sk, poly);
  return FractionalEncodedPoly{SparsePoly{poly}};
}

BalancedEncodedPoly<helib::Ctxt> encrypt(
    const BalancedEncodedPoly<SparsePoly>& encoded_poly,
    const helib::PubKey& pk) {
  const auto poly = encoded_poly.poly().expand();
  const auto view = pk.getContext().getView();
  helib::Ctxt ctxt(pk);
  view.encrypt(ctxt, pk, poly);
  return BalancedEncodedPoly{ctxt, encoded_poly.digit()};
}

BalancedEncodedPoly<SparsePoly> encrypt(
    const BalancedEncodedPoly<helib::Ctxt>& encoded_poly,
    const helib::SecKey& sk) {
  const auto ctxt = encoded_poly.poly();
  std::vector<long> poly;
  const auto view = sk.getContext().getView();
  view.decrypt(ctxt, sk, poly);
  return BalancedEncodedPoly{SparsePoly{poly}, encoded_poly.digit()};
}

BalancedSlotsEncodedPoly<helib::Ctxt> encrypt(
    const BalancedSlotsEncodedPoly<SparsePoly>& encoded_poly,
    const helib::PubKey& pk) {
  const auto poly = encoded_poly.poly().expand();
  const auto view = pk.getContext().getView();
  helib::Ctxt ctxt(pk);
  view.encrypt(ctxt, pk, poly);
  return BalancedSlotsEncodedPoly{ctxt, encoded_poly.digits()};
}

BalancedSlotsEncodedPoly<SparsePoly> encrypt(
    const BalancedSlotsEncodedPoly<helib::Ctxt>& encoded_poly,
    const helib::SecKey& sk) {
  const auto ctxt = encoded_poly.poly();
  std::vector<long> poly;
  const auto view = sk.getContext().getView();
  view.decrypt(ctxt, sk, poly);
  return BalancedSlotsEncodedPoly{SparsePoly{poly}, encoded_poly.digits()};
}

}  // namespace hekit::coder
