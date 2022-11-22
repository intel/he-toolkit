// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <algorithm>
#include <vector>

namespace hekit::coder {

template <typename Poly>
class EncPolyBase {
 public:
  EncPolyBase() = delete;
  EncPolyBase(const Poly& poly, const std::vector<long>& is)
      : poly_(poly), is_(is) {}
  virtual Poly& poly() { return poly_; }
  virtual const Poly& poly() const { return poly_; }
  auto& i() { return is_; }
  const auto& i() const { return is_; }
  virtual EncPolyBase<Poly> operator+(const EncPolyBase<Poly>& rhs) const {
    throw std::logic_error("EncPolyBase addition not implemented");
  }

 private:
  Poly poly_;
  std::vector<long> is_;
};

template <typename Poly>
class EncPolyBalanced : public EncPolyBase<Poly> {
 public:
  EncPolyBalanced() = delete;
  EncPolyBalanced(const Poly& poly, const std::vector<long>& is)
      : EncPolyBase<Poly>{poly, is} {}

  EncPolyBase<Poly> operator+(const EncPolyBase<Poly>& rhs) const override {
    const auto& lhs = *this;
    EncPolyBalanced<Poly> tmp(rhs.poly(), rhs.i());
    long in = std::abs(lhs.i().front() - rhs.i().front());
    tmp.poly() = (lhs.i().front() < rhs.i().front())
                     ? lhs.poly() + shift(rhs.poly(), in)
                     : shift(lhs.poly(), in) + rhs.poly();

    tmp.i().push_back(std::max(lhs.i().front(), rhs.i().front()));
    return tmp;
  }
};

template <typename Poly>
class EncPolyMultiBalanced : public EncPolyBase<Poly> {
 public:
  EncPolyMultiBalanced() = delete;
  EncPolyMultiBalanced(const std::vector<Poly>& polys,
                       const std::vector<long>& is)
      : EncPolyBase<Poly>{polys, is} {}
};

template <typename Poly>
class EncPolyFrac : public EncPolyBase<Poly> {
 public:
  EncPolyFrac() = delete;
  EncPolyFrac(const Poly& poly) : EncPolyBase<Poly>{poly, {}} {}

  EncPolyBase<Poly> operator+(const EncPolyBase<Poly>& rhs) const override {
    auto& lhs = *this;
    return EncPolyFrac<Poly>{lhs.poly() + rhs.poly()};
  }
};

template <typename Poly, typename Nums>
struct Coder {
  virtual EncPolyBase<Poly> encode(const Nums& nums) const = 0;
  virtual Nums decode(const EncPolyBase<Poly>& enc_poly) const = 0;
  virtual ~Coder() = default;
};

template <typename OutPoly, typename Nums>
inline EncPolyBase<OutPoly> encode(const Nums& nums,
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
