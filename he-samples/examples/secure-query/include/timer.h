// Copyright (C) 2020-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include <chrono>
#include <iostream>

namespace intel {
namespace Common {

/**
 * \class Timer
 * \details
 *
 * This class provides operations to track time.
 *
 *
 **/
class Timer {
 public:
  /**
   * @brief Constructor for the Timer Class
   * @param high_precision - flag to use high precision for time
   * @param start_active   - flag to start timer instantly
   */
  Timer(bool high_precision = false, bool start_active = false) {
    m_active = false;
    m_high_precision_mode = high_precision;
    if (start_active == true) {
      start();
    }
  }

  /**
   * @brief start timer instantly
   */
  void start() {
    if (m_high_precision_mode)
      m_high_start_time = std::chrono::high_resolution_clock::now();
    else
      m_start_time = std::chrono::system_clock::now();

    m_active = true;
  }

  /**
   * @brief stop timer instantly
   */
  void stop() {
    if (m_high_precision_mode)
      m_high_end_time = std::chrono::high_resolution_clock::now();
    else
      m_end_time = std::chrono::system_clock::now();

    m_active = false;
  }

  /**
   * @brief indicate the timer is active or not
   * @return boolean - status of the timer
   */
  bool isActive() { return m_active; }

  /**
   * @brief number of ellapse time that timer is holding
   * @param micro - indicates returning in ms or micro-second
   * @return number of elappsed milli-second or micro-second
   */
  double elapsedMilliseconds(bool micro = false) {
    std::chrono::time_point<std::chrono::system_clock> endTime;
    std::chrono::time_point<std::chrono::high_resolution_clock> highEndTime;

    if (m_active) {
      if (m_high_precision_mode)
        highEndTime = std::chrono::high_resolution_clock::now();
      else
        endTime = std::chrono::system_clock::now();
    } else {
      if (m_high_precision_mode)
        highEndTime = m_high_end_time;
      else
        endTime = m_end_time;
    }

    if (micro == false) {
      if (m_high_precision_mode)
        return std::chrono::duration<double, std::milli>(highEndTime -
                                                         m_high_start_time)
            .count();
      else
        return std::chrono::duration<double, std::milli>(endTime - m_start_time)
            .count();
    } else {
      if (m_high_precision_mode)
        return std::chrono::duration<double, std::micro>(highEndTime -
                                                         m_high_start_time)
            .count();
      else
        return std::chrono::duration<double, std::micro>(endTime - m_start_time)
            .count();
    }
  }

  /**
   * @brief number of elapse time that timer is holding
   * @return number of elapsed second
   */
  double elapsedSeconds() { return elapsedMilliseconds() / 1000.0; }

  /**
   * @brief number of elapse time that timer is holding
   * @return number of elappsed micro second
   */
  double elapsedMicroSeconds() { return elapsedMilliseconds(true); }

 private:
  // Standard
  std::chrono::time_point<std::chrono::system_clock> m_start_time;
  std::chrono::time_point<std::chrono::system_clock> m_end_time;

  // High
  std::chrono::time_point<std::chrono::high_resolution_clock> m_high_start_time;
  std::chrono::time_point<std::chrono::high_resolution_clock> m_high_end_time;

  bool m_active;
  bool m_high_precision_mode;
};

}  // namespace Common
}  // namespace intel
