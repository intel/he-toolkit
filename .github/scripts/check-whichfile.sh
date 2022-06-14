#!/bin/bash
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

SUCCESS=0
FAILURE=1

WHICHFILES="docker/which-files.txt"

if ! git ls-files > "$WHICHFILES"; then
  echo "FAILURE: Something is wrong with git ls-files command."
  exit $FAILURE
fi

if [ -n "$(git diff "$WHICHFILES")" ]; then
  echo "FAILURE: $WHICHFILES was not up to date. Updated now!"
  exit $FAILURE
fi
exit $SUCCESS
