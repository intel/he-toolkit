/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#include <gtest/gtest.h>
#include <helib/helib.h>
#include <helib/partialMatch.h>

#include "io.h"

namespace {

using Ptxt = helib::Ptxt<helib::BGV>;

TEST(TestLookup, ptxtToPtxtComparison) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(100)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);
  Ptxt zero_ptxt(context);

  helib::Matrix<Ptxt> matrix_db(zero_ptxt, 2, 2);
  matrix_db(0, 0) = p1;
  matrix_db(0, 1) = p2;
  matrix_db(1, 0) = p3;
  matrix_db(1, 1) = p4;
  helib::Database<Ptxt> ptxt_db(matrix_db, context);

  helib::Matrix<Ptxt> ptxt_query(zero_ptxt, 1, 2);
  ptxt_query(0, 0) = p3;
  ptxt_query(0, 1) = p4;

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  helib::QueryBuilder qb(a && b);
  auto query = qb.build(ptxt_db.columns());

  auto match = ptxt_db.contains(query, ptxt_query);

  std::vector<long> e1 = {1, 1, 1, 1};
  helib::Matrix<Ptxt> expected_result(zero_ptxt, 2, 1);
  expected_result(1, 0) = Ptxt(context, e1);

  EXPECT_EQ(match.dims(0), expected_result.dims(0));
  EXPECT_EQ(match.dims(1), expected_result.dims(1));

  for (std::size_t i = 0; i < expected_result.dims(0); ++i) {
    for (std::size_t j = 0; j < expected_result.dims(1); ++j) {
      EXPECT_EQ(match(i, j), expected_result(i, j));
    }
  }
}

TEST(TestLookup, ptxtToCtxtComparison) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(1000)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  addFrbMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);

  helib::Ctxt zero_ctxt(pk), c1(pk), c2(pk), c3(pk), c4(pk);
  helib::Matrix<helib::Ctxt> matrix_db(zero_ctxt, 2, 2);
  pk.Encrypt(c1, p1);
  pk.Encrypt(c2, p2);
  pk.Encrypt(c3, p3);
  pk.Encrypt(c4, p4);
  matrix_db(0, 0) = c1;
  matrix_db(0, 1) = c2;
  matrix_db(1, 0) = c3;
  matrix_db(1, 1) = c4;
  helib::Database<helib::Ctxt> ctxt_db(matrix_db, context);

  Ptxt zero_ptxt(context);
  helib::Matrix<Ptxt> ptxt_query(zero_ptxt, 1, 2);
  ptxt_query(0, 0) = p3;
  ptxt_query(0, 1) = p4;

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  helib::QueryBuilder qb(a && b);
  auto query = qb.build(ctxt_db.columns());

  auto match = ctxt_db.contains(query, ptxt_query);

  std::vector<long> e1 = {1, 1, 1, 1};
  helib::Matrix<Ptxt> expected_result(zero_ptxt, 2, 1);
  expected_result(1, 0) = Ptxt(context, e1);

  EXPECT_EQ(match.dims(0), expected_result.dims(0));
  EXPECT_EQ(match.dims(1), expected_result.dims(1));

  for (std::size_t i = 0; i < expected_result.dims(0); ++i) {
    for (std::size_t j = 0; j < expected_result.dims(1); ++j) {
      Ptxt entry(context);
      sk.Decrypt(entry, match(i, j));
      EXPECT_EQ(entry, expected_result(i, j));
    }
  }
}

TEST(TestLookup, ctxtToPtxtComparison) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(1000)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  addFrbMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);
  Ptxt zero_ptxt(context);

  helib::Matrix<Ptxt> matrix_db(zero_ptxt, 2, 2);
  matrix_db(0, 0) = p1;
  matrix_db(0, 1) = p2;
  matrix_db(1, 0) = p3;
  matrix_db(1, 1) = p4;
  helib::Database<Ptxt> ptxt_db(matrix_db, context);

  helib::Ctxt zero_ctxt(pk), c1(pk), c2(pk);
  helib::Matrix<helib::Ctxt> ctxt_query(zero_ctxt, 1, 2);
  pk.Encrypt(c1, p3);
  pk.Encrypt(c2, p4);
  ctxt_query(0, 0) = c1;
  ctxt_query(0, 1) = c2;

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  helib::QueryBuilder qb(a && b);
  auto query = qb.build(ptxt_db.columns());

  auto match = ptxt_db.contains(query, ctxt_query);

  std::vector<long> e1 = {1, 1, 1, 1};
  helib::Matrix<Ptxt> expected_result(zero_ptxt, 2, 1);
  expected_result(1, 0) = Ptxt(context, e1);

  EXPECT_EQ(match.dims(0), expected_result.dims(0));
  EXPECT_EQ(match.dims(1), expected_result.dims(1));

  for (std::size_t i = 0; i < expected_result.dims(0); ++i) {
    for (std::size_t j = 0; j < expected_result.dims(1); ++j) {
      Ptxt entry(context);
      sk.Decrypt(entry, match(i, j));
      EXPECT_EQ(entry, expected_result(i, j));
    }
  }
}

TEST(TestLookup, ctxtToCtxtComparison) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(1000)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  addFrbMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);

  helib::Ctxt zero_ctxt(pk), c1(pk), c2(pk), c3(pk), c4(pk);
  helib::Matrix<helib::Ctxt> matrix_db(zero_ctxt, 2, 2);
  pk.Encrypt(c1, p1);
  pk.Encrypt(c2, p2);
  pk.Encrypt(c3, p3);
  pk.Encrypt(c4, p4);
  matrix_db(0, 0) = c1;
  matrix_db(0, 1) = c2;
  matrix_db(1, 0) = c3;
  matrix_db(1, 1) = c4;
  helib::Database<helib::Ctxt> ctxt_db(matrix_db, context);

  helib::Matrix<helib::Ctxt> ctxt_query(zero_ctxt, 1, 2);
  ctxt_query(0, 0) = c3;
  ctxt_query(0, 1) = c4;

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  helib::QueryBuilder qb(a && b);
  auto query = qb.build(ctxt_db.columns());

  auto match = ctxt_db.contains(query, ctxt_query);

  std::vector<long> e1 = {1, 1, 1, 1};
  helib::Matrix<Ptxt> expected_result(Ptxt(context), 2, 1);
  expected_result(1, 0) = Ptxt(context, e1);

  EXPECT_EQ(match.dims(0), expected_result.dims(0));
  EXPECT_EQ(match.dims(1), expected_result.dims(1));

  for (std::size_t i = 0; i < expected_result.dims(0); ++i) {
    for (std::size_t j = 0; j < expected_result.dims(1); ++j) {
      Ptxt entry(context);
      sk.Decrypt(entry, match(i, j));
      EXPECT_EQ(entry, expected_result(i, j));
    }
  }
}

TEST(TestLookup, throwsWhenQueryHasMoreColumnsThanDatabase) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(1000)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  addFrbMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);

  // Query matrix
  Ptxt zero_ptxt(context);
  helib::Matrix<Ptxt> query_data(zero_ptxt, 1, 3);
  query_data(0, 0) = p1;
  query_data(0, 1) = p2;
  query_data(0, 2) = p2;

  // Database matrix
  helib::Matrix<Ptxt> db_data(zero_ptxt, 2, 2);
  db_data(0, 0) = p1;
  db_data(0, 1) = p2;
  db_data(1, 0) = p3;
  db_data(1, 1) = p4;
  helib::Database<Ptxt> db(db_data, context);

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  helib::QueryBuilder qb(a && b);
  auto query = qb.build(db.columns());

  EXPECT_THROW(db.contains(query, query_data), helib::InvalidArgument);
}

TEST(TestLookup, throwsWhenDatabaseHasMoreColumnsThanQuery) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(1000)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  addFrbMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);

  // Query matrix
  Ptxt zero_ptxt(context);
  helib::Matrix<Ptxt> query_data(zero_ptxt, 1, 2);
  query_data(0, 0) = p1;
  query_data(0, 1) = p2;

  // Database matrix
  helib::Matrix<Ptxt> db_data(zero_ptxt, 2, 3);
  db_data(0, 0) = p1;
  db_data(0, 1) = p2;
  db_data(0, 2) = p2;
  db_data(1, 0) = p3;
  db_data(1, 1) = p4;
  db_data(1, 2) = p4;
  helib::Database<Ptxt> db(db_data, context);

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  const helib::QueryExpr& c = helib::makeQueryExpr(2);
  helib::QueryBuilder qb(a && b && c);
  auto query = qb.build(db.columns());

  EXPECT_THROW(db.contains(query, query_data), helib::InvalidArgument);
}

TEST(TestLookup, throwsWhenQueryBuilderExpectsMoreColumnsThanAvailable) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(1000)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  addFrbMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);

  // Query matrix
  Ptxt zero_ptxt(context);
  helib::Matrix<Ptxt> query_data(zero_ptxt, 1, 2);
  query_data(0, 0) = p1;
  query_data(0, 1) = p2;

  // Database matrix
  helib::Matrix<Ptxt> db_data(zero_ptxt, 2, 2);
  db_data(0, 0) = p1;
  db_data(0, 1) = p2;
  db_data(1, 0) = p3;
  db_data(1, 1) = p4;
  helib::Database<Ptxt> db(db_data, context);

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  const helib::QueryExpr& c = helib::makeQueryExpr(2);
  helib::QueryBuilder qb(a && b && c);

  // Should throw as QueryBuilder expects 3 columns but db.columns == 2
  EXPECT_THROW(qb.build(db.columns()), helib::OutOfRangeError);
}

TEST(TestLookup, throwsWhenQueryHasMoreThanOneRow) {
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                               .m(24)
                               .p(37)
                               .r(1)
                               .bits(1000)
                               .build();
  // clang-format on
  helib::SecKey sk(context);
  sk.GenSecKey();
  addSome1DMatrices(sk);
  addFrbMatrices(sk);
  helib::PubKey& pk = sk;

  std::vector<long> d1 = {1, 2, 3, 4};
  std::vector<long> d2 = {5, 6, 7, 8};
  std::vector<long> d3 = {9, 10, 11, 12};
  std::vector<long> d4 = {13, 14, 15, 16};

  Ptxt p1(context, d1);
  Ptxt p2(context, d2);
  Ptxt p3(context, d3);
  Ptxt p4(context, d4);

  // Query matrix
  Ptxt zero_ptxt(context);
  helib::Matrix<Ptxt> query_data(zero_ptxt, 2, 2);
  query_data(0, 0) = p1;
  query_data(0, 1) = p2;
  query_data(1, 0) = p3;
  query_data(1, 1) = p4;

  // Database matrix
  helib::Matrix<Ptxt> db_data(zero_ptxt, 2, 2);
  db_data(0, 0) = p1;
  db_data(0, 1) = p2;
  db_data(1, 0) = p3;
  db_data(1, 1) = p4;
  helib::Database<Ptxt> db(db_data, context);

  // Build logical query
  const helib::QueryExpr& a = helib::makeQueryExpr(0);
  const helib::QueryExpr& b = helib::makeQueryExpr(1);
  helib::QueryBuilder qb(a && b);
  auto query = qb.build(db.columns());

  // Query is a 2x2 matrix.
  // Code does not support query matrices that contain more than one row
  EXPECT_THROW(db.contains(query, query_data), helib::InvalidArgument);
}

}  // namespace
