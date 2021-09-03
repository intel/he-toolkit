#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#
# Clone repo from given url. Optionally pass branch as second arg.
# If exists locally just update with git pull.
#
git_clone() {
  local -r url="$1"
  local -r branch="$2"
  local -r repo="$(basename "${url%.git}")"
  local opts=""

  if [ -n "$branch" ]; then
    opts="-v -b $branch"
  fi

  if [ ! -d "$repo/.git" ]; then
    # $opts cannot be quoted.
    # shellcheck disable=SC2086
    git clone $opts "$url"
  fi
}
