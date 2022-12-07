# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Tests for yes and no"""


def is_yes(test: str) -> bool:
    """Test for yes"""
    return test.lower() in ("y", "ye", "yes")


def is_no(test: str) -> bool:
    """Test for no"""
    return test.lower() in ("n", "no")
