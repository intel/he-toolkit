// Copyright (C) 2020 Intel Corporation
// SPDX-License-Identifier: Apache-2.0

#ifndef EXAMPLES_LOGISTIC_REGRESSION_KERNELS_OMP_UTILS_H_
#define EXAMPLES_LOGISTIC_REGRESSION_KERNELS_OMP_UTILS_H_

#pragma once

#include <vector>

class OMPUtilities {
 public:
  static int assignOMPThreads(int& remaining_threads, int requested_threads) {
    int retval = (requested_threads > 0 ? requested_threads : 1);
    if (retval > remaining_threads) retval = remaining_threads;
    if (retval > 1)
      remaining_threads -= retval;
    else
      retval = 1;
    return retval;
  }
};

class OMPUtilitiesS : public OMPUtilities {
 public:
  static const int MaxThreads;

  /**
   * @brief Sets number of threads to assign at specified nesting level.
   * @param level[in] OpenMP nesting level.
   * @param threads[in] Number of threads to assign at specified nesting level.
   */
  static void setThreadsAtLevel(int level, int threads);
  /**
   * @brief Retrieves threads at specified level.
   * @param level[in] OpenMP nesting level.
   * @return Number of threads to assign at specified nesting level.
   */
  static int getThreadsAtLevel(int level);
  /**
   * @brief Retrieves threads to assign to current OpenMP nesting level.
   */
  static int getThreadsAtLevel();

 private:
  static std::vector<int> m_threads_per_level;
};

#endif  // EXAMPLES_LOGISTIC_REGRESSION_KERNELS_OMP_UTILS_H_
