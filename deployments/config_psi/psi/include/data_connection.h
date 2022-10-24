/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include "data_record.h"

#include <fstream>
#include <memory>
#include <string>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

// Interface for Data Connection
struct DataConn {
  enum class Type { FILESYS, KAFKA };
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
  virtual void open() const = 0;
  virtual void close() const = 0;
  virtual InDataRecord read() const = 0;
  virtual void write(const OutDataRecord& data) const = 0;
  virtual ~DataConn() = default;
};

// Interface for Data Connection Configuration
struct DataConnConfig {
  virtual ~DataConnConfig() = default;
};

class FileSysConfig : public DataConnConfig {
  // TODO(JC) add attribs required by FileSys
  FileSysConfig(const json& json_config) {}
};

// Concrete class implementing access of a local file system
class FileSys : public DataConn {
 private:
  FileSysConfig config;

 public:
  // Factory method
  FileSys() = delete;
  FileSys(const FileSysConfig& config) : config_(config) { open(config_); }

  void open() override {}

  void close() override {}

  InDataRecord read() override {
    std::ifstream ifs(source);
    Data data(ifs);
    data.read();
    return data;
  }

  void write(const OutDataRecord& data) override { data.write(); }

  ~FileSys() override { disconnect(); }
};
