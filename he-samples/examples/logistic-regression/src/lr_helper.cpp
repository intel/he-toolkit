// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "include/lr_helper.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>

#include "include/data_loader.hpp"
#include "kernels/omp_utils.h"

namespace lrhelper {
template <>
inline double sigmoid<3>(const double x) {
  return 0.5 + 0.15012 * x - 0.001593008 * std::pow(x, 3);
}

template <>
inline double sigmoid<7>(const double x) {
  return 0.5 - 0.21687 * x + 0.008191543 * std::pow(x, 3) -
         0.000165833 * std::pow(x, 5) + 0.00001196 * std::pow(x, 7);
}

double minus_logsigmoid_poly4(const double x) {
  return -1.0 *
         (0.000527 * std::pow(x, 4) - 0.0822 * std::pow(x, 2) + 0.5 * x - 0.78);
}

void get_init_weight(const std::vector<std::vector<double>>& data,
                     const std::vector<double>& target,
                     std::vector<double>& out_weight, double& out_bias) {
  if (data.size() != target.size())
    throw std::invalid_argument("Data and target size mismatch");

  if (data.size() < 1 || target.size() < 1)
    throw std::invalid_argument("Data/target is empty");

  for (size_t i = 0; i < data.size(); ++i) {
    if (data[i].empty())
      throw std::invalid_argument("Data[" + std::to_string(i) + "] is empty");
  }

  double n_data = static_cast<double>(data.size());
  size_t n_features = data[0].size();

  std::vector<std::vector<double>> x_body;
  std::vector<double> x_bias;

  get_z(data, target, x_body, x_bias);

  out_bias = std::accumulate(x_bias.begin(), x_bias.end(), 0.0) / n_data;
  out_weight = std::vector<double>(n_features, 0.0);
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t j = 0; j < n_features; ++j) {
    for (size_t i = 0; i < x_body.size(); ++i) out_weight[j] += x_body[i][j];
    out_weight[j] = out_weight[j] / n_data;
  }
}

void get_z(const std::vector<std::vector<double>>& X,
           const std::vector<double>& y,
           std::vector<std::vector<double>>& out_z_main,
           std::vector<double>& out_z_bias) {
  if (X.size() != y.size())
    throw std::invalid_argument("X and y size mismatch");

  std::vector<double> _y;
  std::transform(
      y.begin(), y.end(), std::back_inserter(_y),
      [](const int& val) { return 2.0 * static_cast<double>(val) - 1.0; });

  out_z_bias = _y;

  out_z_main.resize(X.size());
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < out_z_main.size(); ++i) {
    double ty = _y[i];
    std::transform(X[i].begin(), X[i].end(), std::back_inserter(out_z_main[i]),
                   [ty](const double& val) { return ty * val; });
  }
}

std::vector<double> get_zw(const std::vector<std::vector<double>>& X,
                           const std::vector<double>& X_bias,
                           const std::vector<double>& W, const double bias) {
  if (X.size() != X_bias.size())
    throw std::invalid_argument("X and X_bias size mismatch");

  if (X.size() < 1 || X_bias.size() < 1)
    throw std::invalid_argument("Input size is empty");

  if (X[0].size() != W.size())
    throw std::invalid_argument("Feature size mismatch");

  std::vector<double> retval(X.size());
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < X.size(); ++i) {
    retval[i] = std::inner_product(X[i].begin(), X[i].end(), W.begin(),
                                   X_bias[i] * bias);
  }

  return retval;
}

std::map<std::string, std::vector<double>> get_lgd(
    const std::vector<std::vector<double>>& X, const std::vector<double>& y,
    const std::vector<double>& W, const double& bias,
    unsigned int sigmoid_degree) {
  std::map<std::string, std::vector<double>> retval;

  double n = static_cast<double>(X.size());
  size_t n_features = W.size();

  std::vector<std::vector<double>> _x;
  std::vector<double> _xb;

  get_z(X, y, _x, _xb);
  std::vector<double> zw = get_zw(_x, _xb, W, bias);

  std::vector<double> logsig4_zw;
  std::transform(zw.begin(), zw.end(), std::back_inserter(logsig4_zw),
                 minus_logsigmoid_poly4);
  retval["loss"] = std::vector<double>{
      std::accumulate(logsig4_zw.begin(), logsig4_zw.end(), 0.0) / n};

  std::vector<double> dw;
  switch (sigmoid_degree) {
    case 7:
      std::transform(zw.begin(), zw.end(), std::back_inserter(dw),
                     [](const double& val) { return sigmoid<7>(-1.0 * val); });
      break;
    default:
      std::transform(zw.begin(), zw.end(), std::back_inserter(dw),
                     [](const double& val) { return sigmoid<3>(-1.0 * val); });
      break;
  }

  std::vector<std::vector<double>> dzw(static_cast<size_t>(n));
  std::vector<double> dzb(static_cast<size_t>(n));

#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < static_cast<size_t>(n); ++i) {
    double dwi = dw[i];
    std::transform(_x[i].begin(), _x[i].end(), std::back_inserter(dzw[i]),
                   [dwi](double& val) { return dwi * val; });
    dzb[i] = dwi * _xb[i];
  }

  retval["djw"] = std::vector<double>(n_features, 0.0);
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t j = 0; j < n_features; ++j) {
    for (size_t i = 0; i < static_cast<size_t>(n); ++i) {
      retval["djw"][j] -= dzw[i][j];
    }
    retval["djw"][j] /= n;
  }

  retval["djb"] = std::vector<double>{
      (-1.0) * std::accumulate(dzb.begin(), dzb.end(), 0.0) / n};

  return retval;
}

std::map<std::string, double> get_evalmetrics(
    const std::vector<double>& expected, const std::vector<double>& predicted) {
  if (expected.size() != predicted.size())
    throw std::invalid_argument("Expected and Predicted size mismatch");

  std::map<std::string, double> retval;
  double tp = 0, tn = 0, fp = 0, fn = 0;

  for (size_t i = 0; i < expected.size(); ++i) {
    if (expected[i] == 1.0 && predicted[i] == 1.0)
      tp++;
    else if (expected[i] == 1 && predicted[i] == 0.0)
      fn++;
    else if (expected[i] == 0 && predicted[i] == 1.0)
      fp++;
    else
      tn++;
  }

  retval["acc"] = (tp + tn) / (tp + fp + tn + fn);
  if (tp + fp > 0)
    retval["precision"] = tp / (tp + fp);
  else
    retval["precision"] = 0.0;

  if (tp + fn > 0)
    retval["recall"] = tp / (tp + fn);
  else
    retval["recall"] = 0.0;

  if (retval["precision"] + retval["recall"] == 0)
    retval["f1"] = 0.0;
  else
    retval["f1"] = (retval["precision"] * retval["recall"]) /
                   (retval["precision"] + retval["recall"]);

  return retval;
}

std::vector<double> test(const std::vector<std::vector<double>>& X,
                         const std::vector<double>& W, const double bias,
                         bool clipResult, bool linear_regression) {
  if (X.size() < 1) throw std::invalid_argument("Input data cannot be empty");

  std::vector<double> retval(X.size());

  for (size_t i = 0; i < X.size(); ++i)
    retval[i] = std::inner_product(X[i].begin(), X[i].end(), W.begin(), bias);

  if (!linear_regression)
    std::transform(retval.begin(), retval.end(), retval.begin(), sigmoid<3>);

  if (clipResult)
    std::transform(
        retval.begin(), retval.end(), retval.begin(),
        [](const double& val) { return static_cast<int>(val + 0.5); });

  return retval;
}
}  // namespace lrhelper
