# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from os import getcwd, chdir

from .context import hekit, command_list, command_remove, command_install
from hekit import main
from command_list import list_components, _SEP_SPACES
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
    mock_input.side_effect = [args_fetch.toml_arg_version, args_fetch.toml_arg_build]

    arg1 = f"{args_fetch.component}/{args_fetch.instance}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)
    assert 2 == mock_input.call_count


def test_command_list_after_fetch(mocker, args_list, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_list, ""
    mock_print = mocker.patch("command_list.print")

    width, arg1 = get_width_and_arg1(args_list.component, args_list.instance)
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
    mock_input.side_effect = [args_build.toml_arg_version, args_build.toml_arg_build]

    arg1 = f"{args_build.component}/{args_build.instance}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)
    assert 2 == mock_input.call_count


def test_command_list_after_build(mocker, args_list, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_list, ""
    mock_print = mocker.patch("command_list.print")

    width, arg1 = get_width_and_arg1(args_list.component, args_list.instance)
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
    mock_input.side_effect = [
        args_install.toml_arg_version,
        args_install.toml_arg_build,
    ]

    arg1 = f"{args_install.component}/{args_install.instance}"

    """Act"""
    main()

    """Assert"""
    mock_print.assert_called_with(arg1)
    assert 2 == mock_input.call_count


def test_command_list_after_install(mocker, args_list, restore_pwd):
    """Arrange"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_list, ""
    mock_print = mocker.patch("command_list.print")

    width, arg1 = get_width_and_arg1(args_list.component, args_list.instance)
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
        # back substitution
        self.recipe_arg = {"name": self.instance}
        self.toml_arg_version = self.instance
        self.toml_arg_build = "build"


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


def get_width_and_arg1(comp: str, inst: str, separation_spaces: int = _SEP_SPACES):
    width = 10
    width_comp = len(comp) + separation_spaces
    width_inst = len(inst) + separation_spaces

    return width, f"{comp:{width_comp}} {inst:{width_inst}}"
