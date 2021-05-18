# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#------------------------------------------------------------------------------
# Examples
#------------------------------------------------------------------------------
if (${ENABLE_SEAL})
        add_subdirectory(secure-query)
else()
        message(STATUS "BUILDING WITHOUT SEAL: Secure Query example WILL NOT be built")
endif()
