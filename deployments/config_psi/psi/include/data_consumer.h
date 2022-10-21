/* Copyright (C) 2022 Intel Corporation
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

template <typename DataType>
class Data {
 private:
  std::fstream fileStream;
  DataType data;

 public:
  Data(const std::ifstream& fileStream) : fileStream(fileStream) {}

  void read() {
    // Read blob of data?
    data.read(fileStream);
  }

  void write() {
    // Write blob of data?
    data.write(fileStream);
  }

  DataType getData() const { return data; }
}
