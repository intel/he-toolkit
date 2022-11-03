/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <fstream>
#include <map>
#include <string>

using Metadata = std::map<std::string, std::string>;

struct DataRecord {
  virtual void read(char* data, size_t size) = 0;
  virtual void write(char* data, size_t size) = 0;
  virtual void write(std::istream& stream) = 0;
  virtual std::string metadata(const std::string& name) const = 0;
  virtual std::stringstream& data_stream() = 0;
};

class FileRecord : public DataRecord {
 private:
  std::fstream file_stream_;
  Metadata metadata_;

  void openForRead(const std::string& filename,
                   const std::string& metadata_filename) {
    file_stream_.open(filename, std::ios::binary | std::ios::in);
    metadata_["source"] = filename;
    metadata_["meta_source"] = metadata_filename;
    auto ifs =
        std::ifstream(metadata_filename, std::ios::binary | std::ios::in);
    std::stringstream ss;
    std::string line;
    while (std::getline(ifs, line)) {
      ss << line;
    }
    // TODO(JC) This needs to get the key dynamically
    metadata_["heql"] = ss.str();
  }

  void openForRead(const std::string& filename) {
    file_stream_.open(filename, std::ios::binary | std::ios::in);
    metadata_["source"] = filename;
  }

  void openForWrite(const std::string& filename) {
    file_stream_.open(filename, std::ios::binary | std::ios::out);
    metadata_["source"] = filename;
  }

 public:
  FileRecord(const std::string& filename, const std::string& mode,
             const std::string& metadata_filename = "") {
    if (mode == "read") {
      (metadata_filename.empty()) ? openForRead(filename)
                                  : openForRead(filename, metadata_filename);
      return;
    }

    if (mode == "write") {
      openForWrite(filename);
      return;
    }

    std::ostringstream msg;
    msg << "Unknown file mode '" << mode << "'";
    throw std::runtime_error(msg.str());
  }

  void read(char* data, size_t size) override { file_stream_.read(data, size); }

  void write(char* data, size_t size) override {
    file_stream_.write(data, size);
  }

  void write(std::istream& stream) override {}

  std::string metadata(const std::string& name) const override {
    return metadata_.at(name);
  }

  std::stringstream& data_stream() override {
    throw std::logic_error("Not implemented");
  }
};

class KafkaRecord : public DataRecord {
 private:
  std::stringstream data_stream_{std::ios::in | std::ios::out |
                                 std::ios::binary};
  Metadata metadata_;

 public:
  KafkaRecord(const Metadata& metadata) : metadata_(metadata) {}

  // Not implementing for now
  void read(char* data, size_t size) override {}

  void write(char* data, size_t size) override {
    data_stream_.write(data, size);
  }

  // This is for copying a buffer
  void write(std::istream& stream) override {
    data_stream_ << stream.rdbuf();
    std::cout << "BUFFER:\n" << data_stream_.str() << std::endl;
  }

  std::string metadata(const std::string& name) const override {
    return metadata_.at(name);
  }

  std::stringstream& data_stream() override { return data_stream_; }
};
