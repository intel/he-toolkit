/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#include <fstream>
#include <memory>
#include <string>

#include <nlohmann/json.hpp>

#pragma once

using json = nlohmann::json;

// Pure abstract class (interface)
class DataConn {
 public:
  // Connect to data layer
  virtual void connect() const = 0;

  // Disconnect from data layer
  virtual void disconnect() const = 0;

  // Read in data
  virtual void read() const = 0;

  // Write out data
  virtual void write() const = 0;

  // Process data
  virtual void process() const = 0;

  virtual ~DataConn() = default;
};

// Concrete class implementing behaviour of a local file system
class FileSys : public DataConn {
 private:
  std::string source;

 public:
  FileSys(const json& config) : source(config.at("source").get<std::string>()) {
    connect();
  }

  void connect() {}

  void disconnect() {}

  template <typename T>
  void read(T& out, const helib::PubKey& pk) {
    out = std::make_unique<T>(readQueryFromFile<T>(source, pk));
  }

  template <typename T>
  void write(const T& out) {
    writeResultsToFile(source, out, /*offset=*/0);
  }

  void process() {}

  ~FileSys() { disconnect(); }
};

// Factory method that creates the FileSys concrete class
DataConn* factory(const std::string& data_conn_type, const json& config) {
  if (data_conn_type == "filesys") {
    return new FileSys(config);
  } else {
    throw std::runtime_error("Invalid data connection '" + data_conn_type +
                             "'");
  }
}
