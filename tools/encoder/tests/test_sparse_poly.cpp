// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../sparse_poly.h"

namespace {

using hekit::coder::SparsePoly;

TEST(sparse_poly, test_zero_poly) {
  const auto& poly = SparsePoly();
  EXPECT_EQ(poly.degree(), 0L);
  EXPECT_EQ(poly[0], 0.0);
}

TEST(sparse_poly, test_assign_terms) {
  const auto& terms = std::map<long, long>({{2, 2}, {3, 1}, {5, 3}});
  const auto& poly = SparsePoly(terms);
  EXPECT_EQ(poly.degree(), 5L);
  for (const auto& [index, coeff] : terms) {
    EXPECT_EQ(poly[index], coeff);
  }
}

TEST(sparse_poly, test_to_string) {
  const auto& poly = SparsePoly({{2, 2}, {3, 1}, {5, 3}});
  ASSERT_STREQ(poly.toString().c_str(), "2x^2 + 1x^3 + 3x^5");
}

TEST(sparse_poly, test_addition) {
  const auto& p1 = SparsePoly({{2, 2}, {3, 1}, {5, 3}});
  const auto& p2 = SparsePoly({{2, 4}, {1, 1}});
  auto sum = p1 + p2;
  ASSERT_STREQ(sum.toString().c_str(), "1x^1 + 6x^2 + 1x^3 + 3x^5")
      << "(" << p1.toString() << ") * (" << p2.toString() << ")";
}

TEST(sparse_poly, test_multiplication_one_term) {
  const auto& p1 = SparsePoly({{2, 2}, {3, 1}, {5, 3}});
  const auto& p2 = SparsePoly(std::map<long, long>{{2, 4}});
  auto prod = p1 * p2;
  ASSERT_STREQ(prod.toString().c_str(), "8x^4 + 4x^5 + 12x^7")
      << "(" << p1.toString() << ") * (" << p2.toString() << ")";
}

TEST(sparse_poly, test_multiplication) {
  const auto& p1 = SparsePoly({{2, 2}, {3, 1}, {5, 3}});
  const auto& p2 = SparsePoly({{2, 4}, {1, 1}});
  auto prod = p1 * p2;
  ASSERT_STREQ(prod.toString().c_str(), "2x^3 + 9x^4 + 4x^5 + 3x^6 + 12x^7")
      << "(" << p1.toString() << ") * (" << p2.toString() << ")";
}

TEST(sparse_poly, test_is_laurent) {
  const auto& poly = SparsePoly({{-2, 2}, {3, 1}, {5, 3}});
  ASSERT_TRUE(poly.is_laurent());
}

TEST(sparse_poly, test_is_not_laurent) {
  const auto& poly = SparsePoly({{2, 2}, {3, 1}, {5, 3}});
  ASSERT_FALSE(poly.is_laurent());
}

TEST(sparse_poly, test_expand) {
  const auto& poly = SparsePoly({{2, 2}, {3, 1}, {5, 3}});
  const auto expanded = poly.expand();
  for (long i = 0; i < expanded.size(); ++i) {
    EXPECT_EQ(expanded[i], poly.coeff(i));
  }
}

}  // namespace
