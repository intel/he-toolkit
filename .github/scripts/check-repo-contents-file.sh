#!/bin/bash
# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

SUCCESS=0
FAILURE=1

REPO_CONTENTS_FILE="$1"

# Check file exists
if [ ! -f "$REPO_CONTENTS_FILE" ]; then
  echo "FAILURE: File '$REPO_CONTENTS_FILE' does not exist."
  exit $FAILURE
fi

# Generate new file, overwrite old file
if ! git ls-files > "$REPO_CONTENTS_FILE"; then
  echo "FAILURE: Something is wrong with git ls-files command."
  exit $FAILURE
fi

# Check if file has changed
if [ -n "$(git diff -- "$REPO_CONTENTS_FILE")" ]; then
  echo "FAILURE: $REPO_CONTENTS_FILE was not up to date. Updated now!"
  exit $FAILURE
fi

exit $SUCCESS
