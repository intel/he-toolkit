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

// across single poly
// num -> poly  == (poly, 0)
// num -> (poly, i)
// nums -> (poly, is)

// template<typename OutPoly, typename Nums>
// OutPoly encode(Nums nums, const Coder& coder){
//   return convert<OutPoly>(coder.encode(nums));
// }

// const Coder& coder = NIBNAFCoder(1.2, 0.00001);
// auto enc_poly = encode<ZZX>(input_num | in_vector, coder);
// OR auto enc_poly = encode<ZZX>(input_num | in_vector, NIBNAFCoder(1.2,
// 0.0001)); auto dec_num_or_vec = decode<ZZX>(input_poly, coder);
// ??? auto enc_poly = encode<Ctxt>(input_num | in_vector, coder);
// ??? auto dec_num_or_vec = decode<Ctxt>(input_poly, coder)

}  // namespace hekit::coder
