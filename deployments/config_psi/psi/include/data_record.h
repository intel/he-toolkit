/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <fstream>
#include <map>
#include <string>

struct DataRecord {
  virtual void read(char* data, size_t size) = 0;
  virtual void write(char* data, size_t size) = 0;
  virtual std::string metadata(const std::string& name) const = 0;
};

class FileRecord : public DataRecord {
 private:
  std::fstream file_stream_;
  std::map<std::string, std::string> metadata_;

  std::ios_base::openmode modeFromString(const std::string& mode_string) {
    if (mode_string == "read") {
      return std::ios::binary | std::ios::in;
    }
    if (mode_string == "write") {
      return std::ios::binary | std::ios::out;
    }
    if (mode_string == "duplex") {
      return std::ios::binary | std::ios::in | std::ios::out;
    }
    throw std::runtime_error("Unknown file mode '" + mode_string + "'");
  }

 public:
  FileRecord(const std::string& filename, const std::string& metadata_filename,
             const std::string& mode) {
    file_stream_.open(filename, modeFromString(mode));
    metadata_["source"] = filename;
    auto ifs = std::ifstream(metadata_filename, modeFromString(mode));
    std::stringstream ss;
    std::string line;
    while (std::getline(ifs, line)) {
      ss << line;
    }
    // TODO(JC) This needs to get the key dynamically
    metadata_["heql"] = ss.str();
  }

  void read(char* data, size_t size) override { file_stream_.read(data, size); }

  void write(char* data, size_t size) override {
    file_stream_.write(data, size);
  }

  std::string metadata(const std::string& name) const override {
    return metadata_.at(name);
  }
};
