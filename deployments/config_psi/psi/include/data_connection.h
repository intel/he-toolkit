/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include "data_record.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <map>
#include <memory>
#include <string>
#include <utility>
#include <vector>

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
  virtual std::unique_ptr<DataRecord> read() const = 0;
  virtual void write(const DataRecord& data) const = 0;
  virtual ~DataConn() = default;
};

// Interface for Data Connection Configuration
struct DataConnConfig {
  virtual ~DataConnConfig() = default;
};

class FileSysConfig : public DataConnConfig {
 private:
  std::string directory_;
  std::string extension_;
  std::string meta_ext_;
  std::string mode_;

 public:
  FileSysConfig(const json& json_config) {
    json_config.at("directory").get_to(directory_);
    json_config.at("ext").get_to(extension_);
    json_config.at("meta_ext").get_to(meta_ext_);

    // TODO(JC) Use correct stream modes
    if (json_config.at("io") == "read") {
      mode_ = "read";
    } else if (json_config.at("io") == "write") {
      mode_ = "write";
    } else {
      throw std::runtime_error("Invalid io argument '" + json_config.at("io") +
                               "'");
    }
  }

  std::string directory() const { return directory_; }
  std::set extensions() const { return extensions_; }
  std::string mode() const { return mode_; }
};

// Concrete class implementing access of a local file system
class FileSys : public DataConn {
 private:
  using fs = std::filesystem;
  FileSysConfig config_;
  std::vector<std::pair<fs::directory_entry, fs::directory_entry>> filenames_;

 public:
  // Factory method
  FileSys() = delete;
  FileSys(const FileSysConfig& config) : config_(config) { open(config_); }

  void open() override {
    auto dir = config.querySource();
    auto it = filesystem::directory_iterator(dir);
    std::vector<std::string> filenames;
    std::copy_if(it, {}, filenames.begin(), [](const auto& filepath) {
      return filepath.is_regular_file() &&
             config_.extensions().contains(filepath.path().extension());
    });
    std::sort(filenames.begin(), filenames.end());

    if (filenames.size() % 2 == 1) {
      throw std::runtime_error("Some files do not have matching metadata.");
    }
    for (long i = 0; i < filenames.size(); i += 2) {
      if (filenames[i].path().stem() != filenames[i + 1].path().stem()) {
        throw std::runtime_error("File has no matching metadata or data.");
      }
      filenames_.emplace_back(filenames[i], filenames[i + 1]);
    }
  }

  void close() override {}  // This is supposed to do nothing

  std::unique_ptr<DataRecord> read() override {
    return FileRecord(filenames_.path().string(), config_.mode());
  }

  // Currently this will do nothing because the file will already exist for PSI
  // but the behaviour could change in the future.
  void write(const DataRecord& data) override {}
};
