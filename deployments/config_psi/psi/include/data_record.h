/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

class InDataRecord {
 public:
  void read() = 0;
};

class OutDataRecord {
 public:
  void write() = 0;
};

class InFileRecord : public InDataRecord {
 private:
  std::ifstream file_stream_;

 public:
  InFileRecord(const std::ifstream& file_stream) : file_stream_(file_stream) {}

  void read() override { file_stream_.read(); }

  auto& stream() { return file_stream_; }
};

class OutFileRecord : public OutDataRecord {
 private:
  std::ofstream file_stream_;

 public:
  OutFileRecord(const std::ofstream& file_stream) : file_stream_(file_stream) {}

  void write(const char* data, size_t size) override {
    // Write blob of data?
    file_stream_.write(data, size);
  }

  auto& stream() { return file_stream_; }
};
