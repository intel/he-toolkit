# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from os import getcwd, chdir
from sys import stderr
from pathlib import Path
from kit.hekit import main
from kit.commands.install import install_components


def test_main_config_is_symlink(mocker, args_fetch):
    """Arrange"""
    args_fetch.config = f"{args_fetch.tests_path}/input_files/default_symlink.config"
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.hekit.print")

    arg1 = f"{args_fetch.component}/{args_fetch.instance}"

    """Act"""
    with pytest.raises(SystemExit):
        main()

    """Assert"""
    mock_print.assert_called_with(
        "Error while running subcommand\n",
        "TypeError('The config file cannot be a symlink')",
        file=stderr,
    )


def test_main_config_name_has_null(mocker, args_fetch):
    """Arrange"""
    args_fetch.config = f"{args_fetch.tests_path}/input_files/web.xml\0default.config"
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.hekit.print")

    arg1 = f"{args_fetch.component}/{args_fetch.instance}"

    """Act"""
    with pytest.raises(SystemExit):
        main()

    """Assert"""
    mock_print.assert_called_with(
        "Error while running subcommand\n",
        "ConfigFileError('Error while parsing config file\\n', \"  ValueError('embedded null byte')\")",
        file=stderr,
    )


def test_main_toml_is_symlink(mocker, args_fetch):
    """Arrange"""
    args_fetch.recipe_file = f"{args_fetch.tests_path}/input_files/test_symlink.toml"
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    main()

    """Assert"""
    message = "TypeError('The TOML file cannot be a symlink')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


def test_main_toml_name_has_null(mocker, args_fetch):
    """Arrange"""
    args_fetch.recipe_file = f"{args_fetch.tests_path}/input_files/web.xml\0test.toml"
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    main()

    """Assert"""
    message = "ValueError('embedded null byte')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


def test_main_toml_wrong_format(mocker, args_fetch):
    """Arrange"""
    args_fetch.recipe_file = (
        f"{args_fetch.tests_path}/input_files/test_wrong_format.toml"
    )
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    """Act"""
    main()

    """Assert"""
    message = "TypeError('replace() argument 2 must be str, not float')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


def test_main_toml_missing_value(mocker, args_fetch):
    """Arrange"""
    args_fetch.recipe_file = (
        f"{args_fetch.tests_path}/input_files/test_missing_value.toml"
    )
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    """Act"""
    main()

    """Assert"""
    message = "TomlDecodeError('Empty value is invalid (line 7 column 1 char 122)')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


def test_main_toml_missing_quotes(mocker, args_fetch):
    """Arrange"""
    args_fetch.recipe_file = (
        f"{args_fetch.tests_path}/input_files/test_missing_quotes.toml"
    )
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    """Act"""
    main()

    """Assert"""
    message = "TomlDecodeError('Unbalanced quotes (line 9 column 24 char 234)')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, fn, upto_stage):
        self.tests_path = Path(__file__).resolve().parent
        self.version = False
        self.component = "hexl"
        self.instance = "1.2.3"
        self.config = f"{self.tests_path}/input_files/default.config"
        self.recipe_file = f"{self.tests_path}/input_files/test.toml"
        self.fn = fn
        self.upto_stage = upto_stage
        self.force = False
        self.all = False
        self.y = True
        # back substitution
        self.recipe_arg = {"name": self.instance}
        self.toml_arg_version = self.instance
        self.toml_arg_build = "build"


@pytest.fixture
def args_fetch():
    return MockArgs(install_components, "fetch")
