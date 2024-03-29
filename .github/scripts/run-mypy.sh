#!/bin/bash
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

SUCCESS=0
FAILURE=1

if ! type -p mypy > /dev/null; then
  echo "FAILURE: mypy not found."
  exit $FAILURE
fi

# shellcheck disable=SC2068
if ! MYPYPATH=kit mypy $@ --ignore-missing-imports; then
  echo "FAILURE: mypy failed. You need to manually correct the errors."
  exit $FAILURE
fi

exit $SUCCESS
