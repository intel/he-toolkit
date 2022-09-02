// Copyright (C) 2022 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <gtest/gtest.h>

#include <iomanip>
#include <iostream>
#include <map>

#include "../sparse_poly.h"

using hekit::poly::SparsePoly;

TEST(spare_poly, test_zero_poly) {
  const auto& poly = SparsePoly();
  EXPECT_EQ(poly.degree(), 0L);
  EXPECT_EQ(poly[0], 0.0);
}

TEST(spare_poly, test_assign_terms) {
  const auto& terms = std::map<long, long>({{2, 2}, {3, 1}, {5, 3}});
  const auto& poly = SparsePoly(terms);
  EXPECT_EQ(poly.degree(), 5L);
  for (const auto& [index, coeff] : terms) {
    EXPECT_EQ(poly[index], coeff);
  }
}

TEST(spare_poly, test_to_string) {
  const auto& poly = SparsePoly({{2, 2}, {3, 1}, {5, 3}});
  ASSERT_STREQ(poly.toString().c_str(), "2x^2 + 1x^3 + 3x^5");
}
