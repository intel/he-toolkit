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
  bool ptxtQuery = false;
  bool ptxtDB = false;
  bool isColumn = false;
  long nthreads = 1;
  long offset = 0;
  bool singleRun = false;
};

// eg: { he_data: {
//         data_source: filesys,
//         config: { source: filepath }
//       },
//       db: {
//         data_source: filesys,
//         type: ptxt/ctxt,
//         config: { source: filepath }
//       },
//       query: {
//         type: ptxt/ctxt,
//         data_source: filesys,
//         config: { source: filepath, table: filepath }
//       },
//       output: {
//         data_source: filesys,
//         config: {source: filepath }
//       }
//     }
//

// Read in JSON config file
void loadConfigFile(CmdLineOpts& options) {
  std::fstream configFile(options.configFilePath);
  auto config = json::parse(configFile);

  config.at("he_data").at("config").at("source").get_to(options.pkFilePath);
  config.at("db").at("config").at("source").get_to(options.databaseFilePath);
  config.at("query").at("config").at("source").get_to(options.queryFilePath);
  config.at("query").at("config").at("table").get_to(options.tableFilePath);
  config.at("output").at("config").at("source").get_to(options.outFilePath);

  if (config.at("db").at("type") == "ptxt") {
    options.ptxtDB = true;
  }

  if (config.at("query").at("type") == "ptxt") {
    options.ptxtQuery = true;
  }
}

// Create filesys concrete class
// DataConn* factory(const std::string& data_conn_type, const json_obj&
// config) {
//   if (data_conn_type == "filesys") {
//     return new FileSys(config);
//   } else {
//     throw runtime_error("Invalid data connection '" + data_conn_type +
//     "'");
//   }
// }

// if (config.at("he_data").at("data_source") == "filesys") {
//   return new FileSys(config);
// } else {
//   throw runtime_error("Invalid data connection '" +
//   config.at("he_data").at("data_source") + "'");
// }
