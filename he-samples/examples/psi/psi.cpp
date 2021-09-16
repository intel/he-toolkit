// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#include <helib/ArgMap.h>
#include <helib/helib.h>
#include <helib/set.h>  // <- set intersection

#include <bitset>
#include <fstream>

using Ptxt = helib::Ptxt<helib::BGV>;

static inline NTL::ZZX binary_to_poly(long x) {
  constexpr long N = 16;
  std::bitset<N> b(x);
  NTL::ZZX poly;

  for (long i = 0; i < N; ++i) {
    SetCoeff(poly, i, b[i]);
  }

  return poly;
}

void read_in_set(std::vector<NTL::ZZX>& out, const std::string& filename) {
  std::ifstream file(filename);
  if (!file.is_open())
    throw std::runtime_error("File '" + filename + "' not found.");
  out.clear();
  std::string line;
  while (std::getline(file, line)) {
    out.emplace_back(std::stoi(line));
  }
}

struct CmdLineOpts {
  std::string client_set_path;
  long m = 771;
  long bits = 1000;
  long nthreads = 1;
  bool ptxt = false;  // Default value
};

int main(int argc, char** argv) {
  CmdLineOpts cmdline_opts;
  // clang-format off
  helib::ArgMap()
    .required()
    .positional()
      .arg("<client-set>", cmdline_opts.client_set_path, "Query file.", nullptr)
    .named()
    .optional()
      .arg("-n", cmdline_opts.nthreads, "Number of threads.")
      .arg("--ptxt", cmdline_opts.ptxt, "Keep client set in encoded plaintext.")
      .arg("--m", cmdline_opts.m,
           "Change the order of the cyclotomic polynomial.")
      .arg("--bits", cmdline_opts.bits, "Change number of big Q bits.")
    .parse(argc, argv);
  // clang-format on

  if (cmdline_opts.nthreads < 1) {
    std::cerr << "Number of threads must be a positive integer. Setting n = 1."
              << std::endl;
    cmdline_opts.nthreads = 1;
  }

  NTL::SetNumThreads(cmdline_opts.nthreads);

  // Create context and keys
  // clang-format off
  helib::Context context = helib::ContextBuilder<helib::BGV>()
                             .m(cmdline_opts.m)
                             .p(2)
                             .r(1)
                             .bits(cmdline_opts.bits)
                             .build();
  // clang-format on

  helib::SecKey secretKey(context);
  secretKey.GenSecKey();

  const helib::PubKey& publicKey = secretKey;  // In HElib pk is a child of sk
  helib::addSome1DMatrices(secretKey);
  helib::addFrbMatrices(secretKey);
  const helib::EncryptedArray& ea = context.getEA();

  // Load things
  // create client set - single ctxt
  std::vector<NTL::ZZX> client_set;
  read_in_set(client_set, cmdline_opts.client_set_path);

  // Encode the client set into a Ptxt
  Ptxt client_set_in_ptxt(context, client_set);

  // Create server set - simple array
  std::vector<NTL::ZZX> server_set;
  read_in_set(server_set, "server.txt");

  Ptxt result(context);
  try {
    if (cmdline_opts.ptxt) {
      // Set intersect
      result = helib::calculateSetIntersection(client_set_in_ptxt, server_set);
    } else {
      helib::Ctxt encrypted_client_set(publicKey);
      publicKey.Encrypt(encrypted_client_set, client_set_in_ptxt);
      // Set intersect
      auto encrypted_result =
          helib::calculateSetIntersection(encrypted_client_set, server_set);
      // Decrypt result
      secretKey.Decrypt(result, encrypted_result);
    }
  } catch (std::runtime_error e) {
    std::cout << e.what() << std::endl;
    std::exit(1);
  }

  // Print out intersection
  for (long i = 0; result.lsize(); ++i) {
    std::cout << result[i] << "\n";
  }
  std::cout << std::endl;

  return 0;
}
