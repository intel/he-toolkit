# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#------------------------------------------------------------------------------
# Examples
#------------------------------------------------------------------------------
if (${ENABLE_SEAL})
  add_subdirectory(secure-query)
  add_subdirectory(logistic-regression)
else()
  message(STATUS "BUILDING WITHOUT SEAL: Secure Query and Logistic Regression examples WILL NOT be built")
endif()

if (${ENABLE_HELIB})
  add_subdirectory(psi)
else()
  message(STATUS "BUILDING WITHOUT HELIB: Private Set Intersection example WILL NOT be built")
endif()
