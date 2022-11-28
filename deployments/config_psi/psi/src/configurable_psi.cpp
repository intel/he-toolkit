/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#include <helib/ArgMap.h>
#include <helib/Matrix.h>

#include <helib/helib.h>
#include <helib/partialMatch.h>
#include <helib/set.h>
#include <io.h>

#include <chrono>   // Debug
#include <csignal>  // std::signal
#include <filesystem>
#include <iostream>
#include <iterator>
#include <thread>       // Debug
#include <type_traits>  // std::decay

#include "data_connection.h"
#include "read_config.h"

using sharedContext = std::shared_ptr<helib::Context>;
template <typename Key>
using uniqueKey = std::unique_ptr<const Key>;
template <typename T>
using uniqueDB = std::unique_ptr<const helib::Database<T>>;

using QueryCtxt = helib::Ctxt;
using QueryPtxt = Ptxt;
using DbCtxt = helib::Ctxt;
using DbPtxt = Ptxt;

namespace fs = std::filesystem;

// Global signal status
namespace {
volatile std::sig_atomic_t g_signal_status = false;
}  // namespace

// Capture signal and change status
void signal_handler(int signal) {
  std::cout << "\n\n*** External interrupt detected! ***\n\n";
  g_signal_status = true;
}

// Update CmdLineOpts with the paths to the input query and HEQL data.
void update_opts_input(CmdLineOpts& cmdLineOpts, const DataRecord& record) {
  cmdLineOpts.queryFilePath = record.metadata("source");
  cmdLineOpts.tableFilePath = record.metadata("meta_source");
}

// Update CmdLineOpts with the path to the outFile.
void update_opts_output(CmdLineOpts& cmdLineOpts) {
  auto filepath = fs::path(cmdLineOpts.queryFilePath);
  cmdLineOpts.outConfig.at("directory").get_to(cmdLineOpts.outFilePath);
  cmdLineOpts.outFilename = fs::path(cmdLineOpts.outFilePath) /
                            filepath.replace_extension(".result").filename();
}

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

// Read in data from a file and write it to the output DataRecord object.
void writeDataToRecord(DataRecord& out_record, const std::string& filename) {
  std::ifstream ifs(filename, std::ios::binary);
  if (!ifs.is_open()) {
    std::ostringstream msg;
    msg << "Could not open file '" << filename << "'";
    throw std::runtime_error(msg.str());
  }
  std::istreambuf_iterator<char> it{ifs};
  std::vector<char> buffer{it, {}};
  // This is the buffer not the stream
  out_record.write(buffer.data(), buffer.size());
}

// Perform a database lookup given query data, HEQL query and database.
template <typename QueryTxt, typename DbTxt>
void databaseLookup(sharedContext& contextp, const helib::PubKey& pk,
                    const helib::QueryType& query, DataRecord& query_record,
                    const helib::Database<DbTxt>& database,
                    CmdLineOpts& cmdLineOpts) {
  // Read in the query data
  std::cout << "Reading query data from file '" << cmdLineOpts.queryFilePath
            << "' ...";
  std::string s(query_record.data(), query_record.size());
  helib::Matrix<QueryTxt> query_data(QueryTxt{pk});
  if (cmdLineOpts.queryConnType == Type::KAFKA) {
    // TODO(JC) this may create unneccesary copies
    query_data = readQueryFromStream<QueryTxt>(
        make_stream_dispenser<std::stringstream>(s), pk);
  } else {
    query_data = readQueryFromFile<QueryTxt>(cmdLineOpts.queryFilePath, pk);
  }
  std::cout << "Done.\n";

  // Perform query lookup
  std::cout << "Performing database lookup...";
  auto match = database.contains(query, query_data);
  std::cout << "Done.\n";

  if constexpr (std::is_same_v<QueryTxt, QueryCtxt> ||
                std::is_same_v<DbTxt, DbCtxt>) {
    // Perform cleanup of all resultant ctxts.
    // Relinearize, reduce, then drop special and small primes.
    match.apply([](auto& x) { x.cleanUp(); });
  }

  // Sum resultant mask(s) into single mask w.r.t. query
  auto sum = binSumRows(match);

  // Update cmdLineOpts so it knows the output filename
  update_opts_output(cmdLineOpts);

  // Write result to file
  std::cout << "Writing result to file '" << cmdLineOpts.outFilename << "' ...";
  writeResultsToFile(cmdLineOpts.outFilename, sum, cmdLineOpts.offset);
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
      .arg("<configFile>", cmdLineOpts.configFilePath, "JSON config file.",
           nullptr)
      // .arg("<pkFile>", cmdLineOpts.pkFilePath, "Public Key file.", nullptr)
      // .arg("<tableFile>", cmdLineOpts.tableFilePath,
      // "File containing table description and query string.", nullptr)
      // .arg("<databaseFile>", cmdLineOpts.databaseFilePath, "Database file.",
      // nullptr)
      // .arg("<queryFile>", cmdLineOpts.queryFilePath, "Query file.", nullptr)
      // .arg("<outFile>", cmdLineOpts.outFilePath, "Output file.", nullptr)
      .named()
      .optional()
      .arg("-n", cmdLineOpts.nthreads, "Number of threads.")
      .arg("--offset", cmdLineOpts.offset,
           "Offset in bytes when writing to file.")
      .toggle()
      // .arg("--ptxt-query", cmdLineOpts.ptxtQuery,
      // "Use plaintext query as input.", nullptr)
      // .arg("--ptxt-db", cmdLineOpts.ptxtDB, "Use plaintext DB as input.",
      // nullptr)
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

  // Install a signal handler
  std::signal(SIGINT, signal_handler);

  // Load JSON config file
  std::cout << "Loading config file...";
  // Pass in cmdLineOpts object and update
  try {
    loadConfigFile(cmdLineOpts);
  } catch (const std::exception& e) {
    std::cerr << "\nExit due to invalid JSON config:\n\t" << e.what()
              << std::endl;
    return EXIT_FAILURE;
  }
  std::cout << "Done.\n";
  // Load Context and PubKey
  sharedContext contextp;
  uniqueKey<helib::PubKey> pkp;
  std::cout << "Loading HE Context and Public Key...";
  std::tie(contextp, pkp) =
      loadContextAndKey<helib::PubKey>(cmdLineOpts.pkFilePath);
  std::cout << "Done.\n";

  uniqueDB<Ptxt> ptxt_db_ptr;
  uniqueDB<helib::Ctxt> ctxt_db_ptr;
  // Load DB once
  std::cout << "Reading database from file '" << cmdLineOpts.databaseFilePath
            << "' ...";
  if (cmdLineOpts.ptxtDB) {  // Load ptxt DB
    ptxt_db_ptr = std::make_unique<helib::Database<Ptxt>>(
        readDbFromFile<Ptxt>(cmdLineOpts.databaseFilePath, contextp, *pkp));
  } else {  // Load ctxt DB
    ctxt_db_ptr = std::make_unique<helib::Database<helib::Ctxt>>(
        readDbFromFile<helib::Ctxt>(cmdLineOpts.databaseFilePath, contextp,
                                    *pkp));
  }
  std::cout << "Done.\n";

  auto query_conn =
      makeDataConn(cmdLineOpts.queryConnType, cmdLineOpts.queryConfig);

  do {  // REPL
    // Parse tableFile to build query
    auto query_record_ptr = query_conn->read();
    if (query_record_ptr == nullptr) {
      // std::cerr << "No record (nullptr received)." << std::endl;
      // TODO(JC) Remove sleep
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
      continue;
    }

    std::cout << "Configuring query...";
    // Reading the heql
    std::unique_ptr<const helib::QueryType> query_ptr;
    if (cmdLineOpts.queryConnType == Type::FILESYS) {
      // Assume data to disk
      update_opts_input(cmdLineOpts, *query_record_ptr);
      query_ptr = std::make_unique<helib::QueryType>(
          helib::pseudoParserFromFile(cmdLineOpts.tableFilePath));
    } else {
      query_ptr = std::make_unique<helib::QueryType>(
          helib::pseudoParser(query_record_ptr->metadata("heql")));
    }
    std::cout << "Done.\n";

    // Process query
    if (cmdLineOpts.ptxtQuery && cmdLineOpts.ptxtDB) {
      std::cout << "Executing ptxt-to-ptxt comparison\n";
      databaseLookup<QueryPtxt, DbPtxt>(contextp, *pkp, *query_ptr,
                                        *query_record_ptr, *ptxt_db_ptr,
                                        cmdLineOpts);
    } else if (cmdLineOpts.ptxtQuery && !cmdLineOpts.ptxtDB) {
      std::cout << "Executing ptxt-to-ctxt comparison\n";
      databaseLookup<QueryPtxt, DbCtxt>(contextp, *pkp, *query_ptr,
                                        *query_record_ptr, *ctxt_db_ptr,
                                        cmdLineOpts);
    } else if (!cmdLineOpts.ptxtQuery && cmdLineOpts.ptxtDB) {
      std::cout << "Executing ctxt-to-ptxt comparison\n";
      databaseLookup<QueryCtxt, DbPtxt>(contextp, *pkp, *query_ptr,
                                        *query_record_ptr, *ptxt_db_ptr,
                                        cmdLineOpts);
    } else {
      std::cout << "Executing ctxt-to-ctxt comparison\n";
      databaseLookup<QueryCtxt, DbCtxt>(contextp, *pkp, *query_ptr,
                                        *query_record_ptr, *ctxt_db_ptr,
                                        cmdLineOpts);
    }

    // Create data connection for outfile
    std::unique_ptr<DataConn> out_conn =
        makeDataConn(cmdLineOpts.outConnType, cmdLineOpts.outConfig);
    if (cmdLineOpts.outConnType == Type::KAFKA) {
      auto out_topic = query_record_ptr->metadata("out-topic");
      auto out_record_ptr =
          out_conn->createDataRecord({{"out-topic", out_topic}});
      writeDataToRecord(*out_record_ptr, cmdLineOpts.outFilename);

      out_conn->write(*out_record_ptr);
    }
  } while (!(g_signal_status || cmdLineOpts.singleRun));  // End REPL

  return g_signal_status;
}
