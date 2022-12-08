// Copyright (C) 2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_DATA_LOADER_HPP_
#define HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_DATA_LOADER_HPP_

#pragma once

#include <unistd.h>

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>

enum class CSVState { UnquotedField, QuotedField, QuotedQuote };
enum class DataMode { TRAIN, TEST, EVAL };
enum class WeightType { W, V };

inline bool file_exists(const std::string& fn) {
  const std::filesystem::path p = fn;
  return std::filesystem::exists(p);
}

std::vector<std::string> readCSVRow(const std::string& row);

/// Read CSV file, Excel dialect. Accept "quoted fields ""with quotes"""
std::vector<std::vector<std::string>> readCSV(std::istream& in);

std::vector<std::vector<double>> dataLoader(std::string dataset_name,
                                            DataMode mode);

std::vector<double> weightsLoaderCSV(std::string dataset_name,
                                     WeightType wtype = WeightType::W);

void splitWeights(const std::vector<double>& rawweights,
                  std::vector<double>& out_weight, double& out_bias);
void splitData(const std::vector<std::vector<double>>& rawdata,
               std::vector<std::vector<double>>& out_data,
               std::vector<double>& out_target);

std::vector<std::vector<double>> transpose(
    const std::vector<std::vector<double>>& data);

#endif  // HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_DATA_LOADER_HPP_
