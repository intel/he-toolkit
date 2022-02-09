// Copyright (C) 2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LOGGER_HPP_
#define HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LOGGER_HPP_

#pragma once

#include <chrono>
#include <cstdarg>
#include <fstream>
#include <iostream>
#include <iterator>
#include <sstream>
#include <string>
#include <vector>

struct LogLevel {
  const std::string name;

  LogLevel(const std::string& n) : name(n) {}
  virtual ~LogLevel(void) = default;
};

struct Info : public LogLevel {
  Info(void) : LogLevel("INFO") {}
};

struct Status : public LogLevel {
  Status(void) : LogLevel("STATUS") {}
};

struct Debug : public LogLevel {
  Debug(void) : LogLevel("DEBUG") {}
};

struct Result : public LogLevel {
  Result(void) : LogLevel("RESULT") {}
};

template <typename Level, typename T>
void _LOG(T only) {
  std::cout << only << std::endl;
}

template <typename Level, typename T, typename... args>
void _LOG(T current, args... next) {
  std::string sp = " ";
  if (Level().name == "STATUS")
    sp = ", ";
  else if (Level().name == "RESULT")
    sp = ": ";

  std::cout << current << sp;
  _LOG<Level>(next...);
}

template <typename Level, typename... args>
void LOG(args... to_print) {
  std::cout << Level().name << ": ";
  if (Level().name == "INFO") {
    std::time_t time = std::time(nullptr);
    std::string time_str = std::ctime(&time);
    time_str.pop_back();
    std::cout << time_str << ": ";
  }

  _LOG<Level>(to_print...);
}

struct Point {
  int x;
  int y;
  friend std::ostream& operator<<(std::ostream& out, const Point& p) {
    return out << '{' << p.x << ',' << p.y << '}';
  }
};

template <typename T>
std::ostream& operator<<(std::ostream& out, const std::vector<T>& v) {
  out << "{";
  size_t last = v.size() - 1;
  for (size_t i = 0; i < v.size(); ++i) {
    out << v[i];
    if (i != last) out << ", ";
  }
  out << "}";
  return out;
}

#endif  // HE_SAMPLES_EXAMPLES_LOGISTIC_REGRESSION_INCLUDE_LOGGER_HPP_
