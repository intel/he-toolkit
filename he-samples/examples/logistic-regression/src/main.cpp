// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <iostream>
#include <random>
#include <vector>

#include "gflags/gflags.h"
#include "include/data_loader.hpp"
#include "include/logger.hpp"
#include "include/lr_helper.hpp"
#include "include/lrhe.hpp"
#include "include/timer.hpp"

DEFINE_string(data, "lrtest_mid",
              "Dataset name to test. Files should have preset name "
              "conventions. Current list of pretrained datasets is "
              "[lrtest_small, lrtest_mid, lrtest_large, lrtest_xlarge]. Please "
              "refer to the datasets folder for more information.");

DEFINE_bool(docompare, false,
            "To compare the HE logistic regression inference result with "
            "non-HE results, set to 1(true)");

DEFINE_int32(poly_modulus_degree, 8192,
             "Set polynomial modulus for CKKS context. Determines the batch "
             "size and security level, thus recommended size is 4096~16384. "
             "Must be a power of 2, with the range of [1024, 32768]");

int main(int argc, char** argv) {
  gflags::ParseCommandLineFlags(&argc, &argv, true);

  std::string fn_dataset(FLAGS_data);
  if (FLAGS_poly_modulus_degree < 1024 || FLAGS_poly_modulus_degree > 32768 ||
      (FLAGS_poly_modulus_degree & (FLAGS_poly_modulus_degree - 1)) != 0)
    throw std::invalid_argument(
        "poly_modulus_degree must be power of 2 and within [1024, 32768] "
        "range.");

  kernel::LRHEKernel kernel(FLAGS_poly_modulus_degree, {60, 45, 45, 45, 45, 45},
                            1UL << 45, true, true);
  lrhe::LogisticRegressionHE lrhe(kernel);

  // load eval data for inference
  LOG<Info>("Loading EVAL dataset");
  std::vector<std::vector<double>> rawdata_eval =
      dataLoader(fn_dataset, DataMode::EVAL);
  std::vector<std::vector<double>> evalData;
  std::vector<double> evalTarget;

  // Split data and target from rawdata
  splitData(rawdata_eval, evalData, evalTarget);

  size_t n_inputs = evalData.size();
  size_t n_weights = evalData[0].size();
  LOG<Info>("Input data size:", "(samples)", n_inputs, " (features)",
            n_weights);

  // load pretrained weights and bias
  LOG<Info>("Loading Model");
  std::vector<double> pretrained_weightsbias = weightsLoaderCSV(fn_dataset);
  std::vector<double> pretrained_weights;
  double pretrained_bias;

  // split bias and weights from pretrained model
  splitWeights(pretrained_weightsbias, pretrained_weights, pretrained_bias);
  lrhe.load_weight(pretrained_weights, pretrained_bias);

  // perform inference with test data
  auto lrhe_evalout = lrhe.inference(evalData);

  // evaluate result and get accuracy and f1 score
  auto eval = lrhelper::get_evalmetrics(evalTarget, lrhe_evalout);
  LOG<Info>("HE inference result - accuracy: ", eval["acc"]);

  if (FLAGS_docompare) {  // If docompare==true, compare with non-HE inference
                          // result
    // Get cleartext inference results
    std::vector<double> lr_weights = lrhe.get_weights();
    double lr_bias = lrhe.get_bias();
    auto lrcleartext_evalout = lrhelper::test(evalData, lr_weights, lr_bias);

    // Count mismatch
    int match_ct = n_inputs;
    for (size_t j = 0; j < n_inputs; ++j) {
      if ((lrhe_evalout[j] - lrcleartext_evalout[j]) != 0.0) {
        match_ct--;
      }
    }
    LOG<Info>("Mismatch count with cleartext LR:", match_ct, "out of",
              n_inputs);
  }
  return 0;
}
