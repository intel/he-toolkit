/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#include <helib/ArgMap.h>
#include <helib/Matrix.h>

#include <helib/helib.h>
#include <helib/partialMatch.h>
#include <helib/set.h>
#include <io.h>

#include <iostream>
#include <type_traits>  // std::decay

using sharedContext = std::shared_ptr<helib::Context>;

// Struct to hold command line arguments
struct CmdLineOpts {
  std::string pkFilePath;
  std::string tableFilePath;
  std::string databaseFilePath;
  std::string queryFilePath;
  std::string outFilePath;
  bool ptxtQuery = false;
  bool ptxtDB = false;
  bool isColumn = false;
  long nthreads = 1;
  long offset = 0;
  bool singleRun = false;
};

// Utility function which performs a binary sum of Matrix rows.
// Destructive to `matrix`
template <typename TXT>
helib::Matrix<TXT> binSumRows(helib::Matrix<TXT>& matrix) {
  // Get ref to the underlying data
  // Dangerous - unconst it - but saves on expensive copies
  auto& vec = matrix.data();
  typedef typename std::decay_t<decltype(vec)>& unconst_ref;
  // Do the summation
  helib::binSumReduction(const_cast<unconst_ref>(vec));

  // Result should be a single entry
  return helib::Matrix<TXT>(vec.at(0), 1, 1);
}

// Database lookup where both the query and dabatase are not encrypted.
void plaintextAllLookup(sharedContext& contextp, helib::PubKey& pk,
                        helib::QueryType& query,
                        helib::Database<Ptxt>& database,
                        CmdLineOpts& cmdLineOpts) {
  // Read in the query data
  std::cout << "Reading query data from file " + cmdLineOpts.queryFilePath +
                   " ...";
  helib::Matrix<Ptxt> queryData =
      readQueryFromFile<Ptxt>(cmdLineOpts.queryFilePath, pk);
  std::cout << "Done.\n";

  // Perform query lookup
  std::cout << "Performing database lookup...";
  auto match = database.contains(query, queryData);
  std::cout << "Done.\n";

  // Sum resultant mask(s) into single mask w.r.t. query
  auto sum = binSumRows(match);

  // Write result to file
  std::cout << "Writing result to file " + cmdLineOpts.outFilePath + " ...";
  writeResultsToFile(cmdLineOpts.outFilePath, sum, cmdLineOpts.offset);
  std::cout << "Done.\n";
}

// Database lookup where the query is not encrypted but the dabatase is.
void plaintextQueryLookup(sharedContext& contextp, helib::PubKey& pk,
                          helib::QueryType& query,
                          helib::Database<helib::Ctxt>& database,
                          CmdLineOpts& cmdLineOpts) {
  // Read in the query data
  std::cout << "Reading query data from file " + cmdLineOpts.queryFilePath +
                   " ...";
  helib::Matrix<Ptxt> queryData =
      readQueryFromFile<Ptxt>(cmdLineOpts.queryFilePath, pk);
  std::cout << "Done.\n";

  // Perform cleanup of all resultant ctxts.
  // Relinearize, reduce, then drop special and small primes.
  auto clean = [](auto& x) { x.cleanUp(); };
  // Perform query lookup
  std::cout << "Performing database lookup...";
  auto match = database.contains(query, queryData).apply(clean);
  std::cout << "Done.\n";

  // Sum resultant mask(s) into single mask w.r.t. query
  auto sum = binSumRows(match);

  // Write result to file
  std::cout << "Writing result to file " + cmdLineOpts.outFilePath + " ...";
  writeResultsToFile(cmdLineOpts.outFilePath, sum, cmdLineOpts.offset);
  std::cout << "Done.\n";
}

// Database lookup where the query is encrypted but the dabatase is not.
void plaintextDBLookup(sharedContext& contextp, helib::PubKey& pk,
                       helib::QueryType& query, helib::Database<Ptxt>& database,
                       CmdLineOpts& cmdLineOpts) {
  // Read in the query data
  std::cout << "Reading query data from file " + cmdLineOpts.queryFilePath +
                   " ...";
  helib::Matrix<helib::Ctxt> queryData =
      readQueryFromFile<helib::Ctxt>(cmdLineOpts.queryFilePath, pk);
  std::cout << "Done.\n";

  // Perform cleanup of all resultant ctxts.
  // Relinearize, reduce, then drop special and small primes.
  auto clean = [](auto& x) { x.cleanUp(); };
  // Perform query lookup
  std::cout << "Performing database lookup...";
  auto match = database.contains(query, queryData).apply(clean);
  std::cout << "Done.\n";

  // Sum resultant mask(s) into single mask w.r.t. query
  auto sum = binSumRows(match);

  // Write result to file
  std::cout << "Writing result to file " + cmdLineOpts.outFilePath + " ...";
  writeResultsToFile(cmdLineOpts.outFilePath, sum, cmdLineOpts.offset);
  std::cout << "Done.\n";
}

// Database lookup where both the query and dabatase are encrypted.
void encryptedAllLookup(sharedContext& contextp, helib::PubKey& pk,
                        helib::QueryType& query,
                        helib::Database<helib::Ctxt>& database,
                        CmdLineOpts& cmdLineOpts) {
  // Read in the query data
  std::cout << "Reading query data from file " + cmdLineOpts.queryFilePath +
                   " ...";
  helib::Matrix<helib::Ctxt> queryData =
      readQueryFromFile<helib::Ctxt>(cmdLineOpts.queryFilePath, pk);
  std::cout << "Done.\n";

  // Perform cleanup of all resultant ctxts.
  // Relinearize, reduce, then drop special and small primes.
  auto clean = [](auto& x) { x.cleanUp(); };
  // Perform query lookup
  std::cout << "Performing database lookup...";
  auto match = database.contains(query, queryData).apply(clean);
  std::cout << "Done.\n";

  // Sum resultant mask(s) into single mask w.r.t. query
  auto sum = binSumRows(match);

  // Write result to file
  std::cout << "Writing result to file " + cmdLineOpts.outFilePath + " ...";
  writeResultsToFile(cmdLineOpts.outFilePath, sum, cmdLineOpts.offset);
  std::cout << "Done.\n";
}

int main(int argc, char* argv[]) {
  // PSI Steps
  // 1. Read in context and pk file
  // 2. Read in encrypted/encoded query data file
  // 3. Read in encrypted/encoded DB (file in column order?)
  // 4. Read in Table and Query from file
  // 5. Perform lookup
  // 6. Return encrypted/encoded mask(s)

  /******************** Argument Parsing ************************/

  CmdLineOpts cmdLineOpts;

  helib::ArgMap()
      .separator(helib::ArgMap::Separator::WHITESPACE)
      .required()
      .positional()
      .arg("<pkFile>", cmdLineOpts.pkFilePath, "Public Key file.", nullptr)
      .arg("<tableFile>", cmdLineOpts.tableFilePath,
           "File containing table description and query string.", nullptr)
      .arg("<databaseFile>", cmdLineOpts.databaseFilePath, "Database file.",
           nullptr)
      .arg("<queryFile>", cmdLineOpts.queryFilePath, "Query file.", nullptr)
      .arg("<outFile>", cmdLineOpts.outFilePath, "Output file.", nullptr)
      .named()
      .optional()
      .arg("-n", cmdLineOpts.nthreads, "Number of threads.")
      .arg("--offset", cmdLineOpts.offset,
           "Offset in bytes when writing to file.")
      .toggle()
      .arg("--ptxt-query", cmdLineOpts.ptxtQuery,
           "Use plaintext query as input.", nullptr)
      .arg("--ptxt-db", cmdLineOpts.ptxtDB, "Use plaintext DB as input.",
           nullptr)
      .arg("--column", cmdLineOpts.isColumn,
           "Flag to signify input is in column format.", nullptr)
      .arg("--single-run", cmdLineOpts.singleRun, "Run the service once.",
           nullptr)
      .parse(argc, argv);

  if (cmdLineOpts.nthreads < 1) {
    std::cerr << "Number of threads must be a positive integer. Setting n = 1."
              << std::endl;
    cmdLineOpts.nthreads = 1;
  }

  NTL::SetNumThreads(cmdLineOpts.nthreads);
  std::cout << "Threads available: " << NTL::AvailableThreads() << std::endl;

  /*********************** Main Program **************************/

  // Load Context and PubKey
  sharedContext contextp;
  std::unique_ptr<helib::PubKey> pkp;
  std::cout << "Loading HE Context and Public Key...";
  std::tie(contextp, pkp) =
      loadContextAndKey<helib::PubKey>(cmdLineOpts.pkFilePath);
  std::cout << "Done.\n";

  std::unique_ptr<helib::Database<Ptxt>> ptxt_db_ptr;
  std::unique_ptr<helib::Database<helib::Ctxt>> ctxt_db_ptr;
  // Load DB once
  if (cmdLineOpts.ptxtDB) {  // Load ptxt DB
    std::cout << "Reading database from file " + cmdLineOpts.databaseFilePath +
                     " ...";
    *ptxt_db_ptr =
        readDbFromFile<Ptxt>(cmdLineOpts.databaseFilePath, contextp, *pkp);
    std::cout << "Done.\n";
  } else {  // Load ctxt DB
    std::cout << "Reading database from file " + cmdLineOpts.databaseFilePath +
                     " ...";
    *ctxt_db_ptr = readDbFromFile<helib::Ctxt>(cmdLineOpts.databaseFilePath,
                                               contextp, *pkp);
    std::cout << "Done.\n";
  }

  // Parse tableFile to build query
  std::cout << "Configuring query...";
  auto query = helib::pseudoParserFromFile(cmdLineOpts.tableFilePath);
  std::cout << "Done.\n";

  // REPL
  do {
    if (cmdLineOpts.ptxtQuery && cmdLineOpts.ptxtDB) {
      // Plaintext query and plaintext DB
      std::cout << "Executing ptxt-to-ptxt comparison\n";
      plaintextAllLookup(contextp, *pkp, query, *ptxt_db_ptr, cmdLineOpts);
    } else if (cmdLineOpts.ptxtQuery && !cmdLineOpts.ptxtDB) {
      // Plaintext query and encrypted DB
      std::cout << "Executing ptxt-to-ctxt comparison\n";
      plaintextQueryLookup(contextp, *pkp, query, *ctxt_db_ptr, cmdLineOpts);
    } else if (!cmdLineOpts.ptxtQuery && cmdLineOpts.ptxtDB) {
      // Encrypted query and plaintext DB
      std::cout << "Executing ctxt-to-ptxt comparison\n";
      plaintextDBLookup(contextp, *pkp, query, *ptxt_db_ptr, cmdLineOpts);
    } else {
      // Encrypted query and encrypted DB
      std::cout << "Executing ctxt-to-ctxt comparison\n";
      encryptedAllLookup(contextp, *pkp, query, *ctxt_db_ptr, cmdLineOpts);
    }
  } while (!cmdLineOpts.singleRun);
  // End REPL

  return 0;
}
