/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <fstream>
#include <map>
#include <string>

struct DataRecord {
  void read(const char* data, size_t size) = 0;
  void write(const char* data, size_t size) = 0;
  long size() const = 0;
  std::string metadata(const std::string& name) = 0;
};

class FileRecord : public DataRecord {
 private:
  std::fstream file_stream_;
  std::map<std::string, std::string> metadata_;

 public:
  FileRecord(const std::string& filename, const std::string& metadata_filename,
             const std::string& mode) {
    file_stream_.open(filename, mode);
    metadata_["source"] = filename;
    auto ifs = std::ifstream(metadata_filename, mode);
    std::stringstream ss;
    while (auto line = std::string{}; std::getline(line, ifs)) {
      ss << line;
    }
    // TODO(JC) This needs to get the key dynamically
    metadata_["heql"] = ss.str();
  }

  void read(const char* data, size_t size) override {
    file_stream_.read(data, size);
  }

  void write(const char* data, size_t size) override {
    file_stream_.write(data, size);
  }

  long size() const { return file_streams_.size(); }

  std::string metadata(const std::string& name) override {
    return metadata_.at(name);
  }
};
