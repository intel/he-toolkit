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
    out.emplace_back(binary_to_poly(std::stoi(line)));
  }
}

template <typename T>
void printVector(const std::vector<T>& v) {
  for (long i = 0; i < long(v.size()); ++i) {
    std::cout << v[i] << "\n";
  }
  std::cout << std::endl;
}

struct CmdLineOpts {
  std::string client_set_path;
  long m = 771;
  long bits = 700;
  long nthreads = 1;
  bool ptxt = false;  // Default value
};

int main(int argc, char** argv) {
  CmdLineOpts cmdline_opts;
  // clang-format off
  helib::ArgMap()
    .separator(helib::ArgMap::Separator::WHITESPACE)
    .required()
    .positional()
      .arg("<client-set>", cmdline_opts.client_set_path, "Client set.", nullptr)
    .named()
    .optional()
      .arg("-n", cmdline_opts.nthreads, "Number of threads.")
      .arg("--m", cmdline_opts.m,
           "Change the order of the cyclotomic polynomial.")
      .arg("--bits", cmdline_opts.bits, "Change number of big Q bits.")
    .toggle()
      .arg("--ptxt", cmdline_opts.ptxt,
           "Keep client set in encoded plaintext.", nullptr)
    .parse(argc, argv);
  // clang-format on

  if (cmdline_opts.nthreads < 1) {
    std::cerr << "Number of threads must be a positive integer. Setting n = 1."
              << std::endl;
    cmdline_opts.nthreads = 1;
  }

  NTL::SetNumThreads(cmdline_opts.nthreads);

  std::cout << "Creating context and keys" << std::endl;
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

  std::cout << "Reading in client set" << std::endl;
  // create client set
  std::vector<NTL::ZZX> client_set;
  read_in_set(client_set, cmdline_opts.client_set_path);
  printVector(client_set);

  // Encode the client set into a Ptxt
  Ptxt client_set_in_ptxt(context, client_set);

  std::cout << "Reading in server set" << std::endl;
  // Create server set - simple array
  std::vector<NTL::ZZX> server_set;
  read_in_set(server_set, "server.txt");
  printVector(server_set);

  std::cout << "Performing the set intersection" << std::endl;
  Ptxt result(context);
  try {
    if (cmdline_opts.ptxt) {
      // Set intersect
      result = helib::calculateSetIntersection(client_set_in_ptxt, server_set);
    } else {
      helib::Ctxt encrypted_client_set(publicKey);
      publicKey.Encrypt(encrypted_client_set, client_set_in_ptxt);
      std::cout << "Encrypt" << std::endl;
      // Set intersect
      auto encrypted_result =
          helib::calculateSetIntersection(encrypted_client_set, server_set);
      std::cout << "PSI'd" << std::endl;
      // Decrypt result
      secretKey.Decrypt(result, encrypted_result);
      std::cout << "Decrypt" << std::endl;
    }
  } catch (std::runtime_error e) {
    std::cout << e.what() << std::endl;
    std::exit(1);
  }

  std::cout << "The following were found in both sets" << std::endl;
  std::cout << "Size: " << result.lsize() << std::endl;
  for (long i = 0; i < result.lsize(); ++i) {
    std::cout << result[i] << "\n";
  }
  std::cout << "FIN." << std::endl;

  return 0;
}
