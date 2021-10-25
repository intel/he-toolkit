// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <seal/seal.h>

#include <iostream>
#include <random>
#include <vector>

#include "gflags/gflags.h"
#include "include/data_loader.hpp"
#include "include/logger.hpp"
#include "include/lr_helper.hpp"
#include "include/lrhe.hpp"
#include "include/timer.hpp"

DEFINE_string(
    data, "lrtest_mid",
    "Dataset name to test. Files should have preset name conventions. "
    "Refer to the datasets folder for more information.");

DEFINE_bool(compare, false,
            "Compare the HE logistic regression inference results with "
            "non-HE results.");

DEFINE_int32(poly_modulus_degree, 8192,
             "Set polynomial modulus for CKKS context. Determines the batch "
             "size and security level, thus recommended size is 4096-16384. "
             "Must be a power of 2, with the range of [1024, 32768]");

DEFINE_bool(data_plain, false, "Run with the data as plaintext.");

DEFINE_bool(model_plain, false, "Run with the model as plaintext.");

DEFINE_bool(linear_regression, false,
            "Calculate linear regression instead of logistic regression.");

DEFINE_int32(security_level, 0, "Security level. One of [0, 128, 192, 256].");

DEFINE_string(coeff_modulus, "60,45,45,45,45,60",
              "Coefficient modulus (list of primes). The bit-lengths of the "
              "primes to be generated.");

DEFINE_int32(batch_size, 0,
             "Batch size. 0 = automatic (poly_modulus_degree / 2). Max = "
             "poly_modulus_degree / 2.");

DEFINE_int32(scale, 45, "Scaling parameter defining precision.");

int main(int argc, char** argv) {
  gflags::ParseCommandLineFlags(&argc, &argv, true);

  std::string fn_dataset(FLAGS_data);
  if (FLAGS_poly_modulus_degree < 1024 || FLAGS_poly_modulus_degree > 32768 ||
      (FLAGS_poly_modulus_degree & (FLAGS_poly_modulus_degree - 1)) != 0)
    throw std::invalid_argument(
        "poly_modulus_degree must be power of 2 and within [1024, 32768] "
        "range.");

  if (FLAGS_batch_size < 0 || FLAGS_batch_size > FLAGS_poly_modulus_degree / 2)
    throw std::invalid_argument(
        "batch_size must be between 0 and poly_modulus_degree / 2.");

  seal::sec_level_type sec_level;
  switch (FLAGS_security_level) {
    case 0:
      sec_level = seal::sec_level_type::none;
      break;
    case 128:
      sec_level = seal::sec_level_type::tc128;
      break;
    case 192:
      sec_level = seal::sec_level_type::tc192;
      break;
    case 256:
      sec_level = seal::sec_level_type::tc256;
      break;
    default:
      LOG<Info>("ERROR: Security level must be one of [0, 128, 192, 256].");
      return EXIT_FAILURE;
  }

  std::vector<int> coeff_modulus;
  std::stringstream ss(FLAGS_coeff_modulus);
  for (int i; ss >> i;) {
    coeff_modulus.push_back(i);
    if (ss.peek() == ',') ss.ignore();
  }

  kernel::LRHEKernel kernel(FLAGS_poly_modulus_degree, coeff_modulus,
                            1UL << FLAGS_scale, true, true, sec_level);
  if (FLAGS_data_plain && FLAGS_model_plain) {
    LOG<Info>("ERROR: Either model or data (or both) must be encrypted.");
    return EXIT_FAILURE;
  }
  lrhe::LogisticRegressionHE lrhe(kernel, !FLAGS_data_plain, !FLAGS_model_plain,
                                  FLAGS_linear_regression, FLAGS_batch_size);

  // load eval data for inference
  LOG<Info>("Loading EVAL dataset");
  auto t_started = intel::timer::now();
  std::vector<std::vector<double>> rawdata_eval =
      dataLoader(fn_dataset, DataMode::EVAL);
  std::vector<std::vector<double>> evalData;
  std::vector<double> evalTarget;

  // Split data and target from rawdata
  splitData(rawdata_eval, evalData, evalTarget);

  size_t n_inputs = evalData.size();
  size_t n_weights = evalData[0].size();
  LOG<Info>("Loading EVAL dataset complete",
            "Elapsed(s):", intel::timer::delta(t_started));
  LOG<Info>("Input data size:", "(samples)", n_inputs, " (features)",
            n_weights);

  // load pretrained weights and bias
  LOG<Info>("Loading Model");
  t_started = intel::timer::now();
  std::vector<double> pretrained_weightsbias = weightsLoaderCSV(fn_dataset);
  std::vector<double> pretrained_weights;
  double pretrained_bias;

  // split bias and weights from pretrained model
  splitWeights(pretrained_weightsbias, pretrained_weights, pretrained_bias);
  LOG<Info>("Loading Model complete",
            "Elapsed(s):", intel::timer::delta(t_started));
  lrhe.load_weight(pretrained_weights, pretrained_bias);

  // perform inference with test data
  auto lrhe_evalout = lrhe.inference(evalData);

  // evaluate result and get accuracy and f1 score
  auto eval = lrhelper::get_evalmetrics(evalTarget, lrhe_evalout);
  LOG<Info>("HE inference result - accuracy: ", eval["acc"]);

  if (FLAGS_compare) {  // If compare==true, compare with non-HE inference
                        // result
    // Get cleartext inference results
    auto lrcleartext_evalout =
        lrhelper::test(evalData, pretrained_weights, pretrained_bias, !FLAGS_linear_regression,
                       FLAGS_linear_regression);

    // Count mismatch
    int mismatch_ct = 0;
    for (size_t j = 0; j < n_inputs; ++j) {
      if (lrhe_evalout[j] != lrcleartext_evalout[j]) {
        mismatch_ct++;
      }
    }
    if (mismatch_ct > 0) {
      LOG<Info>("Mismatch count with cleartext LR:", mismatch_ct, "/",
                n_inputs);
    } else {
      LOG<Info>("All match!");
    }
  }
  return 0;
}
