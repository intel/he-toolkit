// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LR_HELPER_HPP_
#define HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LR_HELPER_HPP_

#pragma once

#include <map>
#include <string>
#include <vector>
// Base functionality for logistic regression based on
// Efficient logistic regression training by Bergamaschi et. al
// (https://eprint.iacr.org/2019/425)
namespace lrhelper {

// Compute initial weight with training set
void get_init_weight(const std::vector<std::vector<double>>& data,
                     const std::vector<double>& target,
                     std::vector<double>& out_weight, double& out_bias);

// Polynomial representation of sigmoid function
template <unsigned int degree = 3>
double sigmoid(const double x);

// Polynomial representation of log(sigmoid()) function
double minus_logsigmoid_poly4(const double x);

// Calculates z. For more detail, check https://eprint.iacr.org/2019/425
void get_z(const std::vector<std::vector<double>>& X,
           const std::vector<double>& y,
           std::vector<std::vector<double>>& out_z_main,
           std::vector<double>& out_z_bias);

// Calculates z dot w. For more detail, check https://eprint.iacr.org/2019/425
std::vector<double> get_zw(const std::vector<std::vector<double>>& X,
                           const std::vector<double>& X_bias,
                           const std::vector<double>& W, const double bias);

// Calculate loss and gradient descent
std::map<std::string, std::vector<double>> get_lgd(
    const std::vector<std::vector<double>>& X, const std::vector<double>& y,
    const std::vector<double>& W, const double& bias,
    unsigned int sigmoid_degree = 3);

// Get evaluation metric of model stored in following keys:
// acc(accuracy), f1(f1 score), recall and precision
std::map<std::string, double> get_evalmetrics(
    const std::vector<double>& expected, const std::vector<double>& predicted);

// Performs logistic regression inference in cleartext data
std::vector<double> test(const std::vector<std::vector<double>>& X,
                         const std::vector<double>& W, const double bias,
                         bool clipResult = true,
                         bool linear_regression = false);
}  // namespace lrhelper

#endif  // HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LR_HELPER_HPP_
