# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

add_executable(goldschmidt goldschmidt.cpp)

target_link_libraries(
  goldschmidt
  helib
)
