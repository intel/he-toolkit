# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest

from .context import hekit
from hekit import get_recipe_arg_dict


def test_get_recipe_arg_dict_correct_format():
    """Arrange"""
    act_arg = "key1=value1, key2=value2, key3=value3"
    exc_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}

    """Act"""
    act_dict = get_recipe_arg_dict(act_arg)

    """assert"""
    assert exc_dict == act_dict


def test_get_recipe_arg_dict_duplicated_key():
    """Arrange"""
    act_arg = "key1=value1, key1=value2, key3=value3"
    exc_dict = {"key1": "value2", "key3": "value3"}

    """Act"""
    act_dict = get_recipe_arg_dict(act_arg)

    """assert"""
    assert exc_dict == act_dict


def test_get_recipe_arg_dict_wrong_format():
    """Arrange"""
    act_arg = "key1=value1, key1=value2, key3"

    """Act"""
    with pytest.raises(ValueError) as execinfo:
        get_recipe_arg_dict(act_arg)

    """assert"""
    assert "Wrong format for ['key3']. Expected key=value" == str(execinfo.value)


def test_get_recipe_arg_dict_missing_comma():
    """Arrange"""
    act_arg = "key1=value1 key2=value2, key3=value3"

    """Act"""
    with pytest.raises(ValueError) as execinfo:
        get_recipe_arg_dict(act_arg)

    """assert"""
    assert (
        "Wrong format for ['key1', 'value1key2', 'value2']. Expected key=value"
        == str(execinfo.value)
    )
