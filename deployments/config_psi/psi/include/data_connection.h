/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <fstream>
#include <memory>
#include <string>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

// Interface for Data Connection
struct DataConn {
  virtual void open() const = 0;
  virtual void close() const = 0;
  virtual void Data read() const = 0;
  virtual void write(const Data& data) const = 0;
  virtual ~DataConn() = default;
};

// Interface for Data Connection Configuration
struct DataConnConfig {
  virtual ~DataConnConfig() = default;
};

class FileSysConfig : public DataConnConfig {
  // TODO(JC) add attribs required by FileSys
  DataConnConfig(const json& json_config) {}
};

// Concrete class implementing access of a local file system
class FileSys : public DataConn {
 public:
  enum class Type { FILESYS, KAFKA };

  // Factory method
  static DataConn* make(const Type& conn_type, const json& config) {
    switch (conn_type) {
      case Type::FILESYS:
        return new FileSys(config);
      case Type::KAFKA:
        throw std::logic_error("Data connection for Kafka not implemented");
      default:
        throw std::runtime_error("Invalid data connection '" + data_conn_type +
                                 "'");
    }
  }

  FileSys(const DataConnConfig& config) { connect(config); }

  void connect() override {}

  void disconnect() override {}

  Data read() override {
    std::ifstream ifs(source);
    Data data(ifs);
    data.read();
    return data;
  }

  void write(const Data& data) override { data.write(); }

  ~FileSys() override { disconnect(); }
};
