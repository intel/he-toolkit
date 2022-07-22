# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from unittest import skip
import pytest
from tests.common_utils import create_config_file, execute_process, get_tests_path

from os import getcwd, chdir
from sys import stderr
from pathlib import Path
from kit.hekit import main
from kit.commands.install import install_components


def test_main_config_is_symlink():
    """Verify that the SW will trigger an exception when
    the config file is a symlink"""
    # Arrange
    tests_path = get_tests_path()
    cmd = f"hekit --config {tests_path}/input_files/default_symlink.config list"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "Error while running subcommand" in err
    assert "The config file cannot be a symlink" in err


@skip
def test_main_config_name_has_null():
    """Verify that the SW will trigger an exception when
    the config file has a null character"""
    # Arrange
    tests_path = get_tests_path()
    cmd = f"hekit --config {args_fetch.tests_path}/input_files/web.xml\0default.config list"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "Error while running subcommand" in err
    assert "embedded null byte" in err


def test_main_toml_is_symlink(tmp_path):
    """Verify that the SW will trigger an exception when
    the config file is a symlink"""
    # Arrange
    config_file = create_config_file(tmp_path)
    tests_path = get_tests_path()
    cmd = (
        f"hekit --config {config_file} fetch {tests_path}/input_files/test_symlink.toml"
    )

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "Error while running subcommand" in err
    assert "The TOML file cannot be a symlink" in err


@skip
def test_main_toml_name_has_null(mocker, args_fetch):
    # Arrange
    args_fetch.recipe_file = f"{args_fetch.tests_path}/input_files/web.xml\0test.toml"
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    # Act
    main()

    # Assert
    message = "ValueError('embedded null byte')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


def test_main_toml_wrong_format(mocker, args_fetch):
    # Arrange
    args_fetch.recipe_file = (
        f"{args_fetch.tests_path}/input_files/test_wrong_format.toml"
    )
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    # Act
    main()

    # Assert
    message = "TypeError('replace() argument 2 must be str, not float')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


def test_main_toml_missing_value(mocker, args_fetch):
    # Arrange
    args_fetch.recipe_file = (
        f"{args_fetch.tests_path}/input_files/test_missing_value.toml"
    )
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    # Act
    main()

    # Assert
    message = "TomlDecodeError('Empty value is invalid (line 7 column 1 char 122)')"
    mock_print_main.assert_called_with(
        "Error while running subcommand\n", message, file=stderr
    )
    mock_exit.assert_called_once_with(1)


def test_main_toml_missing_quotes(mocker, args_fetch):
    # Arrange
    args_fetch.recipe_file = (
        f"{args_fetch.tests_path}/input_files/test_missing_quotes.toml"
    )
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_fetch, ""
    mock_print = mocker.patch("kit.commands.install.print")
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_exit = mocker.patch("kit.hekit.sys_exit")

    # Act
    main()

    # Assert
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
