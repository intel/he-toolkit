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
namespace fs = std::filesystem;

// Interface for Data Connection
struct DataConn {
  virtual void open() = 0;
  virtual void close() = 0;
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
      throw std::runtime_error(std::string("Invalid io argument '") +
                               json_config.at("io").get<std::string>() + "'");
    }
  }

  std::string directory() const { return directory_; }
  std::string extension() const { return extension_; }
  std::string meta_ext() const { return meta_ext_; }
  std::string mode() const { return mode_; }
};

// Concrete class implementing access of a local file system
class FileSys : public DataConn {
 private:
  FileSysConfig config_;
  mutable long current_entry_ = 0;
  std::vector<std::pair<fs::directory_entry, fs::directory_entry>> filenames_;

 public:
  // Factory method
  FileSys(const FileSysConfig& config) : config_(config) { open(); }
  FileSys(const json& config) : FileSys(FileSysConfig(config)) {}
  FileSys() = delete;

  void open() override {
    auto it = fs::directory_iterator(config_.directory());
    std::vector<fs::directory_entry> filenames;
    std::copy_if(it, {}, filenames.begin(),
                 [extension = config_.extension(),
                  meta_ext = config_.meta_ext()](const auto& filepath) {
                   return filepath.is_regular_file() &&
                          (extension == filepath.path().extension() ||
                           meta_ext == filepath.path().extension());
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

  std::unique_ptr<DataRecord> read() const override {
    if (current_entry_ >= filenames_.size()) {
      return nullptr;
    }
    auto [filename, metadata_filename] = filenames_.at(current_entry_++);
    auto fn = filename.path().string();
    auto mfn = metadata_filename.path().string();
    return std::make_unique<FileRecord>(fn, mfn, config_.mode());
  }

  // Currently this will do nothing because the file will already exist for PSI
  // but the behaviour could change in the future.
  void write(const DataRecord& data) const override {}
};

enum class Type { FILESYS, KAFKA };

std::string typeToString(const Type& type) {
  switch (type) {
    case Type::FILESYS:
      return "filesys";
    case Type::KAFKA:
      return "kafka";
    default:
      throw std::logic_error("Unknown type.");
  }
}

static std::unique_ptr<DataConn> makeDataConn(const Type& conn_type,
                                              const json& config) {
  switch (conn_type) {
    case Type::FILESYS:
      return std::make_unique<FileSys>(config);
    case Type::KAFKA:
      throw std::logic_error("Data connection for Kafka not implemented");
    default:
      throw std::runtime_error(std::string("Invalid data connection '") +
                               typeToString(conn_type) + "'");
  }
}
