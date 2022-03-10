# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from os import getcwd, chdir

from .context import hekit, config, command_list, command_remove, command_install, spec
from hekit import main, get_recipe_arg_dict
from command_list import list_components
from command_remove import remove_components
from command_install import install_components

# Due to install command changes current directory,
# the other commands need to restore the current path
cwd_test = getcwd()


def test_command_install_fetch(mocker, args_fetch):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("command_install.print")
    mock_input = mocker.patch("spec.input")
    mock_input.return_value = args_fetch.instance

    arg1 = f"{args_fetch.component}/{args_fetch.instance}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)
    mock_input.assert_called_once()


def test_command_list_after_fetch(mocker, args_list, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_list, ""
    mock_print = mocker.patch("command_list.print")

    width = 10
    arg1 = f"{args_list.component:{width}} {args_list.instance:{width}}"
    arg2 = f"{'success':{width}}"
    arg34 = f"{'':{width}}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1, arg2, arg34, arg34)


def test_command_install_build(mocker, args_build):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_build, ""
    mock_print = mocker.patch("command_install.print")
    mock_input = mocker.patch("spec.input")
    mock_input.return_value = args_build.instance

    arg1 = f"{args_build.component}/{args_build.instance}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)
    mock_input.assert_called_once()


def test_command_list_after_build(mocker, args_list, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_list, ""
    mock_print = mocker.patch("command_list.print")

    width = 10
    arg1 = f"{args_list.component:{width}} {args_list.instance:{width}}"
    arg23 = f"{'success':{width}}"
    arg4 = f"{'':{width}}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1, arg23, arg23, arg4)


def test_command_remove_after_build(mocker, args_remove, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_remove, ""
    mock_print = mocker.patch("command_remove.print")

    arg1 = f"Instance '{args_remove.instance}' of component '{args_remove.component}' successfully removed"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)


def test_command_install_execution(mocker, args_install):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_install, ""
    mock_print = mocker.patch("command_install.print")
    mock_input = mocker.patch("spec.input")
    mock_input.return_value = args_install.instance

    arg1 = f"{args_install.component}/{args_install.instance}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)
    mock_input.assert_called_once()


def test_command_list_after_install(mocker, args_list, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_list, ""
    mock_print = mocker.patch("command_list.print")

    width = 10
    arg1 = f"{args_list.component:{width}} {args_list.instance:{width}}"
    arg234 = f"{'success':{width}}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1, arg234, arg234, arg234)


def test_command_remove_after_install(mocker, args_remove, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_remove, ""
    mock_print = mocker.patch("command_remove.print")

    arg1 = f"Instance '{args_remove.instance}' of component '{args_remove.component}' successfully removed"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)


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
    act_arg = "key1=value1 key2=value2, key3"

    """Act"""
    with pytest.raises(ValueError) as execinfo:
        get_recipe_arg_dict(act_arg)

    """assert"""
    assert (
        "Wrong format for ['key1', 'value1key2', 'value2']. Expected key=value"
        == str(execinfo.value)
    )


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, fn, upto_stage):
        self.version = False
        self.component = "hexl"
        self.instance = "1.2.3"
        self.config = "tests/config/default.config"
        self.recipe_file = "tests/config/test.toml"
        self.fn = fn
        self.upto_stage = upto_stage
        self.recipe_arg = {"name": self.instance}


@pytest.fixture
def args_fetch():
    return MockArgs(install_components, "fetch")


@pytest.fixture
def args_build():
    return MockArgs(install_components, "build")


@pytest.fixture
def args_install():
    return MockArgs(install_components, "install")


@pytest.fixture
def args_list():
    return MockArgs(list_components, "")


@pytest.fixture
def args_remove():
    return MockArgs(remove_components, "")


@pytest.fixture
def restore_pwd():
    global cwd_test
    chdir(cwd_test)
