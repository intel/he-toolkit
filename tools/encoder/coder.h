// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <vector>

namespace hekit::coder {

template <typename Poly>
class EncPoly {
 public:
  EncPoly() = delete;
  EncPoly(const Poly& poly, const std::vector<long>& is)
      : poly_(poly), is_(is) {}
  Poly& poly() { return poly_; }
  const Poly& poly() const { return poly_; }
  auto& i() { return is_; }
  const auto& i() const { return is_; }

 private:
  Poly poly_;
  std::vector<long> is_;
};

template <typename Poly, typename Nums>
struct Coder {
  virtual EncPoly<Poly> encode(const Nums& nums) const = 0;
  virtual Nums decode(const EncPoly<Poly>& enc_poly) const = 0;
  virtual ~Coder() = default;
};

template <typename OutPoly, typename Nums>
inline EncPoly<OutPoly> encode(const Nums& nums,
                               const Coder<OutPoly, Nums>& coder) {
  return coder.encode(nums);
}

// template <typename OutPoly, typename MidPoly, typename Nums>
// OutPoly encode(const Nums& nums, const Coder<MidPoly, Nums>& coder) {
//  return convert<OutPoly>(coder.encode(nums));
//}

// template <typename Nums, typename InPoly>
// Nums decode(const InPoly& in_poly, const Coder<InPoly, Nums>& coder) {
//  return coder.decode(in_poly);
//}

// template <typename Nums, typename MidPoly, typename InPoly>
// Nums decode(const InPoly& in_poly, const Coder<MidPoly, Nums>& coder) {
//  return coder.decode(convert<MidPoly>(in_poly));
//}

// across single poly
// num -> poly  == (poly, 0)
// num -> (poly, i)
// nums -> (poly, is)

// const Coder& coder = NIBNAFCoder(1.2, 0.00001);
// auto enc_poly = encode<ZZX>(input_num | in_vector, coder);
// OR auto enc_poly = encode<ZZX>(input_num | in_vector, NIBNAFCoder(1.2,
// 0.0001)); auto dec_num_or_vec = decode<ZZX>(input_poly, coder);
// ??? auto enc_poly = encode<Ctxt>(input_num | in_vector, coder);
// ??? auto dec_num_or_vec = decode<Ctxt>(input_poly, coder)

}  // namespace hekit::coder
