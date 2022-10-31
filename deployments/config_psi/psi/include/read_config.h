/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#include <fstream>
#include <string>
#include <nlohmann/json.hpp>

#pragma once

using json = nlohmann::json;

// Struct to hold command line arguments
struct CmdLineOpts {
  std::string configFilePath;
  std::string pkFilePath;
  std::string tableFilePath;
  std::string databaseFilePath;
  std::string queryFilePath;
  std::string outFilePath;
  json heConfig;
  json dbConfig;
  json queryConfig;
  json outConfig;
  bool ptxtQuery = false;
  bool ptxtDB = false;
  bool isColumn = false;
  long nthreads = 1;
  long offset = 0;
  bool singleRun = false;
};

// eg: { he_data: {
//         data_source: filesys,
//         config: { source: filepath, io: read }
//       },
//       db: {
//         data_source: filesys,
//         type: ptxt/ctxt,
//         config: { source: filepath, io: read }
//       },
//       query: {
//         type: ptxt/ctxt,
//         data_source: filesys,
//         config: { directory: directory, ext: "ctxt", meta_ext: "heql", io:
//         read
//         }
//       },
//       output: {
//         data_source: filesys,
//         config: {directory: filepath, io: write }
//       }
//     }
//
// extension = { ctxt, ptxt, heql }
//
//  KAFKA
//       query: {
//         type: ptxt/ctxt,
//         data_source: kafka,
//         config: {directory: filepath, ext: "ctxt", meta_ext: "heql", topic:
//         "topic-name", broker: "ip:port", io: read
//         }
//       },
//       output: {
//         data_source: kafka,
//         config: {directory: filepath, topic: "topic-name", broker: "ip:port",
//         io: write }
//       }
//
//       KAFKA HEADER
//       TIMESTAMP
//       QL
//       UID
//       BID
//       JID
//

// Read in JSON config file
void loadConfigFile(CmdLineOpts& options) {
  std::fstream configFile(options.configFilePath);
  auto config = json::parse(configFile);

  config.at("he_data").at("config").get_to(options.heConfig);
  options.heConfig.at("source").get_to(options.pkFilePath);
  config.at("db").at("config").get_to(options.dbConfig);
  options.dbConfig.at("source").get_to(options.databaseFilePath);
  config.at("query").at("config").get_to(options.queryConfig);
  // options.queryConfig.at("source").get_to(options.queryFilePath);
  // options.queryConfig.at("table").get_to(options.tableFilePath);
  config.at("output").at("config").get_to(options.outConfig);
  // options.outConfig.at("source").get_to(options.outFilePath);

  if (config.at("db").at("type") == "ptxt") {
    options.ptxtDB = true;
  }

  if (config.at("query").at("type") == "ptxt") {
    options.ptxtQuery = true;
  }
}
