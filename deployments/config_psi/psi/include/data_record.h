/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <fstream>

struct DataRecord {
  void read() = 0;
  void write() = 0;
};

class FileRecord : public DataRecord {
 private:
  std::fstream file_stream_;

 public:
  FileRecord(const std::fstream& file_stream) : file_stream_(file_stream) {}

  void read() override { file_stream_.read(); }

  void write(const char* data, size_t size) override {
    // Write blob of data?
    file_stream_.write(data, size);
  }
};
