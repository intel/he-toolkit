#!/bin/bash
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

SUCCESS=0
FAILURE=1

# Generate new file, overwrite old file
if ! pylint kit; then
  echo "FAILURE: pylint failed. You need to manually correct the errors."
  exit $FAILURE
fi

exit $SUCCESS
