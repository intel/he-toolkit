// Copyright (C) 2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include "lrhe_kernel.hpp"
namespace kernel {
const double LRHEKernel::sigmoid_coeff_3[] = {0.5, 0.15012, 0.0, -0.001593008};
const double LRHEKernel::sigmoid_coeff_5[] = {0.5,        0.19131, 0.0,
                                              -0.0045963, 0.0,     0.000041233};
const double LRHEKernel::sigmoid_coeff_7[] = {
    0.5, -0.21687, 0.0, 0.008191543, 0.0, -0.000165833, 0.0, 0.000001196};

void LRHEKernel::initContext(size_t poly_modulus_degree,
                             std::vector<int> coeff_modulus, double scale,
                             bool generate_relin_keys,
                             bool generate_galois_keys) {
  // SEAL uses an additional 'special prime' coeff modulus for relinearization
  // only. As such, encrypting with N coeff moduli yields a ciphertext with
  // N-1 coeff moduli for computation. See section 2.2.1 in
  // https://arxiv.org/pdf/1908.04172.pdf. So, we add an extra prime for fair
  // comparison against other HE schemes.
  m_scale = scale;
  m_poly_modulus_degree = poly_modulus_degree;

  m_parms.set_poly_modulus_degree(poly_modulus_degree);

  m_parms.set_coeff_modulus(
      seal::CoeffModulus::Create(poly_modulus_degree, coeff_modulus));

  m_context.reset(new seal::SEALContext(m_parms, true, m_sec_level));
  m_keygen = std::make_shared<seal::KeyGenerator>(*m_context);
  m_keygen->create_public_key(m_public_key);
  m_secret_key = m_keygen->secret_key();

  if (generate_relin_keys) {
    m_keygen->create_relin_keys(m_relin_keys);
  }
  if (generate_galois_keys) {
    m_keygen->create_galois_keys(m_galois_keys);
  }

  m_encryptor = std::make_shared<seal::Encryptor>(*m_context, m_public_key);
  m_evaluator = std::make_shared<seal::Evaluator>(*m_context);
  m_decryptor = std::make_shared<seal::Decryptor>(*m_context, m_secret_key);
  m_encoder = std::make_shared<seal::CKKSEncoder>(*m_context);
  m_slot_count = m_encoder->slot_count();
}

seal::Ciphertext LRHEKernel::vecMatProduct(
    const std::vector<seal::Ciphertext>& A_T_extended,
    const std::vector<seal::Ciphertext>& B) {
  size_t rows = A_T_extended.size();

  std::vector<seal::Ciphertext> retval(rows);
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t r = 0; r < rows; ++r) {
    evaluator().multiply(A_T_extended[r], B[r], retval[r]);
  }

  // add all rows
  size_t step = 2;
  while ((step / 2) < rows) {
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
    for (size_t i = 0; i < rows; i += step) {
      if ((i + step / 2) < rows)
        evaluator().add_inplace(retval[i], retval[i + step / 2]);
    }
    step *= 2;
  }

  evaluator().relinearize_inplace(retval[0], m_relin_keys);
  evaluator().rescale_to_next_inplace(retval[0]);

  return retval[0];
}

seal::Ciphertext LRHEKernel::vecMatProduct(
    const std::vector<seal::Ciphertext>& A_T_extended,
    const std::vector<seal::Plaintext>& B) {
  size_t rows = A_T_extended.size();

  std::vector<seal::Ciphertext> retval(rows);
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t r = 0; r < rows; ++r) {
    evaluator().multiply_plain(A_T_extended[r], B[r], retval[r]);
  }

  // add all rows
  size_t step = 2;
  while ((step / 2) < rows) {
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
    for (size_t i = 0; i < rows; i += step) {
      if ((i + step / 2) < rows)
        evaluator().add_inplace(retval[i], retval[i + step / 2]);
    }
    step *= 2;
  }

  evaluator().rescale_to_next_inplace(retval[0]);

  return retval[0];
}

seal::Ciphertext LRHEKernel::vecMatProduct(
    const std::vector<seal::Plaintext>& A_T_extended,
    const std::vector<seal::Ciphertext>& B) {
  size_t rows = A_T_extended.size();

  std::vector<seal::Ciphertext> retval(rows);
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
  for (size_t r = 0; r < rows; ++r) {
    evaluator().multiply_plain(B[r], A_T_extended[r], retval[r]);
  }

  // add all rows
  size_t step = 2;
  while ((step / 2) < rows) {
#pragma omp parallel for num_threads(OMPUtilitiesS::getThreadsAtLevel())
    for (size_t i = 0; i < rows; i += step) {
      if ((i + step / 2) < rows)
        evaluator().add_inplace(retval[i], retval[i + step / 2]);
    }
    step *= 2;
  }

  evaluator().rescale_to_next_inplace(retval[0]);

  return retval[0];
}

seal::Ciphertext LRHEKernel::evaluatePolynomialVector(
    const seal::Ciphertext& inputs, const gsl::span<const double>& coefficients,
    bool is_minus) {
  if (coefficients.empty())
    throw std::invalid_argument("coefficients cannot be empty");

  double multiplier = (is_minus) ? -1.0 : 1.0;

  seal::Ciphertext retval = encrypt(encode(gsl::span(
      std::vector<double>(slot_count(), multiplier * coefficients[0]).data(),
      slot_count())));

  size_t degree = coefficients.size() - 1;

  seal::Ciphertext x_ref = inputs;
  seal::Ciphertext powx = inputs;
  for (size_t d = 1; d <= degree; ++d) {
    if (d > 1) {
      evaluator().multiply_inplace(powx, x_ref);
      evaluator().relinearize_inplace(powx, m_relin_keys);
      evaluator().rescale_to_next_inplace(powx);
      matchLevel(&x_ref, &powx);
    }

    if (coefficients[d] != 0.0) {
      seal::Plaintext pt_coeff = encode(gsl::span(
          std::vector<double>(slot_count(), multiplier * coefficients[d])
              .data(),
          slot_count()));
      seal::Ciphertext buf;

      matchLevel(&powx, &pt_coeff);
      evaluator().multiply_plain(powx, pt_coeff, buf);
      evaluator().rescale_to_next_inplace(buf);

      matchLevel(&retval, &buf);
      buf.scale() = m_scale;
      evaluator().add_inplace(retval, buf);
    }
  }

  return retval;
}

seal::Ciphertext LRHEKernel::evaluatePolynomialVectorHorner(
    const seal::Ciphertext& inputs, const gsl::span<const double>& coefficients,
    bool is_minus) {
  if (coefficients.empty())
    throw std::invalid_argument("coefficients cannot be empty");

  double multiplier = (is_minus) ? -1.0 : 1.0;
  seal::Ciphertext buf = inputs;

  auto it = coefficients.rbegin();
  seal::Ciphertext retval = encrypt(encode(
      gsl::span(std::vector<double>(slot_count(), multiplier * (*it)).data(),
                slot_count())));

  for (++it; it != coefficients.rend(); ++it) {
    matchLevel(&buf, &retval);
    evaluator().multiply_inplace(retval, buf);
    evaluator().relinearize_inplace(retval, m_relin_keys);
    evaluator().rescale_to_next_inplace(retval);

    seal::Plaintext pt_coeff = encode(
        gsl::span(std::vector<double>(slot_count(), multiplier * (*it)).data(),
                  slot_count()));
    matchLevel(&retval, &pt_coeff);
    retval.scale() = m_scale;
    evaluator().add_plain_inplace(retval, pt_coeff);
  }

  return retval;
}

seal::Ciphertext LRHEKernel::evaluateLinearRegressionTransposed(
    std::vector<seal::Ciphertext> weights_T_extended,
    std::vector<seal::Ciphertext>& inputs_T, seal::Ciphertext bias_extended) {
  seal::Ciphertext retval = vecMatProduct(weights_T_extended, inputs_T);

  matchLevel(&retval, &bias_extended);
  bias_extended.scale() = m_scale;
  retval.scale() = m_scale;

  evaluator().add_inplace(retval, bias_extended);

  return retval;
}

seal::Ciphertext LRHEKernel::evaluateLinearRegressionTransposed(
    std::vector<seal::Ciphertext> weights_T_extended,
    std::vector<seal::Plaintext>& inputs_T, seal::Ciphertext bias_extended) {
  seal::Ciphertext retval = vecMatProduct(weights_T_extended, inputs_T);

  matchLevel(&retval, &bias_extended);
  bias_extended.scale() = m_scale;
  retval.scale() = m_scale;

  evaluator().add_inplace(retval, bias_extended);

  return retval;
}

seal::Ciphertext LRHEKernel::evaluateLinearRegressionTransposed(
    std::vector<seal::Plaintext> weights_T_extended,
    std::vector<seal::Ciphertext>& inputs_T, seal::Plaintext bias_extended) {
  seal::Ciphertext retval = vecMatProduct(weights_T_extended, inputs_T);

  matchLevel(&retval, &bias_extended);
  bias_extended.scale() = m_scale;
  retval.scale() = m_scale;

  evaluator().add_plain_inplace(retval, bias_extended);

  return retval;
}

seal::Ciphertext LRHEKernel::evaluateLogisticRegressionTransposed(
    std::vector<seal::Ciphertext> weights_T_extended,
    std::vector<seal::Ciphertext>& inputs_T, seal::Ciphertext bias_extended,
    unsigned int sigmoid_degree) {
  seal::Ciphertext retval = evaluateLinearRegressionTransposed(
      weights_T_extended, inputs_T, bias_extended);

  switch (sigmoid_degree) {
    case 5:
      retval = sigmoid_vector<5>(retval);
      break;
    case 7:
      retval = sigmoid_vector<7>(retval);
      break;
    default:
      retval = sigmoid_vector<3>(retval);
      break;
  }

  return retval;
}

seal::Ciphertext LRHEKernel::evaluateLogisticRegressionTransposed(
    std::vector<seal::Ciphertext> weights_T_extended,
    std::vector<seal::Plaintext>& inputs_T, seal::Ciphertext bias_extended,
    unsigned int sigmoid_degree) {
  seal::Ciphertext retval = evaluateLinearRegressionTransposed(
      weights_T_extended, inputs_T, bias_extended);

  switch (sigmoid_degree) {
    case 5:
      retval = sigmoid_vector<5>(retval);
      break;
    case 7:
      retval = sigmoid_vector<7>(retval);
      break;
    default:
      retval = sigmoid_vector<3>(retval);
      break;
  }

  return retval;
}

seal::Ciphertext LRHEKernel::evaluateLogisticRegressionTransposed(
    std::vector<seal::Plaintext> weights_T_extended,
    std::vector<seal::Ciphertext>& inputs_T, seal::Plaintext bias_extended,
    unsigned int sigmoid_degree) {
  seal::Ciphertext retval = evaluateLinearRegressionTransposed(
      weights_T_extended, inputs_T, bias_extended);

  switch (sigmoid_degree) {
    case 5:
      retval = sigmoid_vector<5>(retval);
      break;
    case 7:
      retval = sigmoid_vector<7>(retval);
      break;
    default:
      retval = sigmoid_vector<3>(retval);
      break;
  }

  return retval;
}

void LRHEKernel::matchLevel(seal::Ciphertext* a, seal::Ciphertext* b) const {
  int a_level = getLevel(*a);
  int b_level = getLevel(*b);
  if (a_level > b_level)
    m_evaluator->mod_switch_to_inplace(*a, b->parms_id());
  else if (a_level < b_level)
    m_evaluator->mod_switch_to_inplace(*b, a->parms_id());
}

void LRHEKernel::matchLevel(seal::Ciphertext* a, seal::Plaintext* b) const {
  int a_level = getLevel(*a);
  int b_level = getLevel(*b);
  if (a_level > b_level)
    m_evaluator->mod_switch_to_inplace(*a, b->parms_id());
  else if (a_level < b_level)
    m_evaluator->mod_switch_to_inplace(*b, a->parms_id());
}

seal::Ciphertext LRHEKernel::accumulate_internal(const seal::Ciphertext& A) {
  seal::Ciphertext retval = A;
  auto max_steps =
      (1 << seal::util::get_significant_bit_count(m_slot_count - 1));
  for (int steps = 1; steps < max_steps; steps <<= 1) {
    seal::Ciphertext rotated;
    evaluator().rotate_vector(retval, steps, m_galois_keys, rotated,
                              seal::MemoryPoolHandle::ThreadLocal());
    evaluator().add_inplace(retval, rotated);
  }
  return retval;
}

seal::Ciphertext LRHEKernel::mean_vector(const std::vector<seal::Ciphertext>& A,
                                         const size_t count) {
  seal::Ciphertext retval = accumulate_chunks(A);
  auto buf = gsl::span(
      std::vector<double>(slot_count(), 1.0 / static_cast<double>(count))
          .data(),
      slot_count());
  seal::Plaintext pt_count = encode(buf);

  matchLevel(&retval, &pt_count);

  evaluator().multiply_plain_inplace(retval, pt_count);
  evaluator().rescale_to_next_inplace(retval);

  retval.scale() = m_scale;

  return retval;
}

seal::Ciphertext LRHEKernel::accumulate_chunks(
    const std::vector<seal::Ciphertext>& A) {
  seal::Ciphertext retval;
  encryptor().encrypt_zero(retval);

  for (size_t i = 0; i < A.size(); ++i) {
    seal::Ciphertext chunk_retval = accumulate_internal(A[i]);
    matchLevel(&retval, &chunk_retval);
    retval.scale() = chunk_retval.scale();
    evaluator().add_inplace(retval, chunk_retval);
  }
  return retval;
}

seal::Plaintext LRHEKernel::encode(const gsl::span<const double>& v) {
  if (v.size() > slot_count())
    throw std::invalid_argument(
        "LRHEKernel::encode: Input vector size is larger than slot_count");

  seal::Plaintext pt_ret;
  m_encoder->encode(v, m_scale, pt_ret);
  return pt_ret;
}

seal::Ciphertext LRHEKernel::encrypt(const seal::Plaintext& v) {
  seal::Ciphertext ct_ret;
  m_encryptor->encrypt(v, ct_ret);
  return ct_ret;
}

seal::Plaintext LRHEKernel::decryptVector(const seal::Ciphertext& v) {
  seal::Plaintext pt_ret;
  m_decryptor->decrypt(v, pt_ret);
  return pt_ret;
}

std::vector<double> LRHEKernel::decodeVector(const seal::Plaintext& v) {
  std::vector<double> ret;
  m_encoder->decode(v, ret);
  return ret;
}

}  // namespace kernel
