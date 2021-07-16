// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "include/data_loader.hpp"

#include "include/logger.hpp"
#include "include/timer.hpp"
#include "kernels/omp_utils.h"

std::vector<std::string> readCSVRow(const std::string& row) {
  CSVState state = CSVState::UnquotedField;
  std::vector<std::string> fields{""};
  size_t i = 0;  // index of the current field
  for (char c : row) {
    switch (state) {
      case CSVState::UnquotedField:
        switch (c) {
          case ',':  // end of field
            fields.push_back("");
            i++;
            break;
          case '"':
            state = CSVState::QuotedField;
            break;
          default:
            fields[i].push_back(c);
            break;
        }
        break;
      case CSVState::QuotedField:
        switch (c) {
          case '"':
            state = CSVState::QuotedQuote;
            break;
          default:
            fields[i].push_back(c);
            break;
        }
        break;
      case CSVState::QuotedQuote:
        switch (c) {
          case ',':  // , after closing quote
            fields.push_back("");
            i++;
            state = CSVState::UnquotedField;
            break;
          case '"':  // "" -> "
            fields[i].push_back('"');
            state = CSVState::QuotedField;
            break;
          default:  // end of quote
            state = CSVState::UnquotedField;
            break;
        }
        break;
    }
  }
  return fields;
}

std::vector<std::vector<std::string>> readCSV(std::istream& in) {
  std::vector<std::vector<std::string>> table;
  std::string row;
  while (!in.eof()) {
    std::getline(in, row);
    if (in.bad() || in.fail()) {
      break;
    }
    auto fields = readCSVRow(row);
    table.push_back(fields);
  }
  return table;
}

std::vector<std::vector<double>> dataLoader(std::string dataset_name,
                                            DataMode mode) {
  std::string suffix;
  switch (mode) {
    case DataMode::TRAIN:
      suffix = "_train.csv";
      break;
    case DataMode::EVAL:
      suffix = "_eval.csv";
      break;
    default:
      suffix = "_test.csv";
  }
  std::string fn = "datasets/" + dataset_name + suffix;

  LOG<Info>("  dataLoader:", fn);

  if (!file_exists(fn)) throw std::runtime_error(fn + " not found");

  std::ifstream ifs(fn);

  std::vector<std::vector<std::string>> rawdata = readCSV(ifs);
  std::vector<std::vector<double>> data(rawdata.size() - 1);

  for (size_t i = 1; i < rawdata.size(); i++) {
    std::transform(rawdata[i].begin(), rawdata[i].end(),
                   std::back_inserter(data[i - 1]),
                   [](const std::string& val) { return std::stod(val); });
  }
  return data;
}

std::vector<double> weightsLoaderCSV(std::string dataset_name,
                                     WeightType wtype) {
  std::string fn = "datasets/" + dataset_name + "_lrmodel.csv";

  LOG<Info>("  weightsLoader:", fn);

  if (!file_exists(fn)) throw std::runtime_error(fn + " not found");
  std::ifstream ifs(fn);

  std::vector<std::vector<std::string>> rawdata = readCSV(ifs);

  std::vector<std::vector<double>> data(rawdata.size());

  for (size_t i = 0; i < rawdata.size(); i++) {
    std::transform(rawdata[i].begin(), rawdata[i].end(),
                   std::back_inserter(data[i]),
                   [](const std::string& val) { return std::stod(val); });
  }
  if (rawdata.size() == 1) return data[0];

  return data[(wtype == WeightType::W) ? 0 : 1];
}

void splitWeights(const std::vector<double>& rawweights,
                  std::vector<double>& out_weight, double& out_bias) {
  out_weight = std::vector<double>(rawweights.begin() + 1, rawweights.end());
  out_bias = rawweights[0];
}

void splitData(const std::vector<std::vector<double>>& rawdata,
               std::vector<std::vector<double>>& out_data,
               std::vector<double>& out_target) {
  size_t sz_rawdata = rawdata.size();
  out_data.resize(sz_rawdata);
  out_target.resize(sz_rawdata);

  for (size_t i = 0; i < sz_rawdata; ++i) {
    out_data[i] = std::vector<double>(rawdata[i].begin(), rawdata[i].end() - 1);
    out_target[i] = *(rawdata[i].end() - 1);
  }
}

std::vector<std::vector<double>> transpose(
    const std::vector<std::vector<double>>& data) {
  std::vector<std::vector<double>> res(data[0].size(),
                                       std::vector<double>(data.size()));

#pragma omp parallel for collapse(2) \
    num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t i = 0; i < data[0].size(); i++) {
    for (size_t j = 0; j < data.size(); j++) {
      res[i][j] = data[j][i];
    }
  }
  return res;
}
