// Copyright (C) 2023 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <helib/helib.h>

#include <algorithm>
#include <vector>

namespace hekit::coder {

// HElib objects tend not to have out-of-place ops i.e. Ctxt
template <typename TXTR>
inline helib::Ctxt operator*(const helib::Ctxt& lhs, const TXTR& rhs) {
  auto ans = lhs;
  ans *= rhs;
  return ans;
}

template <typename TXTR>
inline helib::Ctxt operator+(const helib::Ctxt& lhs, const TXTR& rhs) {
  auto ans = lhs;
  ans += rhs;
  return ans;
}

inline helib::Ctxt shift(const helib::Ctxt& poly, long digit) {
  auto ctxt = poly;
  NTL::ZZX x;
  SetCoeff(x, digit);
  // FIXME HElib's APIs are slot-centric. Temp work around
  // encrypt and multiply.
  helib::Ctxt x_encrypted(ctxt.getPubKey());
  ctxt.getPubKey().Encrypt(x_encrypted, x);
  //  std::cerr << "digit: " << digit << ", shift by x poly: "<< x << std::endl;
  //  const auto& context = ctxt.getContext();
  //  helib::PtxtArray ptxt(context);
  //  ptxt = x;
  ctxt *= x_encrypted;
  return ctxt;
}

inline auto select(const helib::Ctxt& lpoly, const helib::Ctxt& rpoly,
                   const std::vector<long>& select_mask) {
  // Given a mask for the slots output selected poly and its complimentary poly
  std::vector<long> complimentary_mask = select_mask;
  std::for_each(complimentary_mask.begin(), complimentary_mask.end(),
                [](auto& bit) { bit = !bit; });

  const auto& context = lpoly.getContext();
  helib::PtxtArray selected_ptxt(context, select_mask);
  helib::PtxtArray complimentary_ptxt(context, complimentary_mask);

  auto selected = (lpoly * selected_ptxt) + (rpoly * complimentary_ptxt);
  auto complimentary = (lpoly * complimentary_ptxt) + (rpoly * selected_ptxt);

  return std::pair{selected, complimentary};
}

inline helib::Ctxt shift(const helib::Ctxt& poly,
                         const std::vector<long>& digits) {
  std::vector<NTL::ZZX> shifts(digits.size());
  for (long i = 0; i < digits.size(); ++i) {
    SetCoeff(shifts[i], digits[i]);
  }

  helib::PtxtArray ptxt(poly.getContext());
  ptxt.load(shifts);
  auto ctxt = poly;
  ctxt *= ptxt;

  return ctxt;
  //  SparsePoly tem{};
  //  for (const auto& [index, value] : poly) {
  //    tem[index + i] = value;
  //  }
  //  return tem;
}

}  // namespace hekit::coder
