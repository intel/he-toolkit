#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#
# Clone repo from given url. Optionally pass branch as second arg.
# If exists locally just update with git pull.
#
git_clone() {
    local url=$1
    local branch=$2
    local repo=$(basename ${url%.git})
    local opts=""

    if [ ! -z "$branch" ]; then
        opts="-v -b $branch"
    fi

    if [ ! -d "$repo/.git" ]; then
        git clone $opts $url
    else
        (cd $repo && git pull --ff-only)
    fi
}
