# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from sys import stderr
from kit.hekit import main
from tests.common_utils import (
    create_config_file,
    execute_process,
    hekit_path,
    input_files_path,
)
from kit.commands.install import install_components


def test_main_config_is_symlink(hekit_path, input_files_path):
    """Verify that the SW triggers an exception when
    the config file is a symlink"""
    cmd = f"{hekit_path} --config {input_files_path}/default_symlink.config list"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert "default_symlink.config cannot be a symlink" in act_result.stderr
    assert 0 != act_result.returncode


def test_main_config_name_has_null(mocker, input_files_path):
    """Verify that the SW triggers an exception when
    the name of the config file has a null character"""
    args = MockArgs()
    args.config = f"{input_files_path}/web.xml\0default.config"
    args.recipe_file = f"{input_files_path}/test.toml"
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print = mocker.patch("kit.hekit.print")
    mock_file_exists = mocker.patch("kit.utils.files.file_exists")
    mock_file_exists.return_value = True
    with pytest.raises(SystemExit) as exc_info:
        main()
    mock_print.assert_called_with(
        "Error while running subcommand\n",
        "ConfigFileError('Error while parsing config file\\n', \"  ValueError('embedded null byte')\")",
        file=stderr,
    )
    assert 0 != exc_info.value.code


def test_main_toml_is_symlink(tmp_path, hekit_path, input_files_path):
    """Verify that the SW triggers an exception when
    the recipe file is a symlink"""
    config_file = create_config_file(tmp_path)
    cmd = f"{hekit_path} --config {config_file} fetch {input_files_path}/test_symlink.toml"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert "The TOML file cannot be a symlink" in act_result.stderr
    assert 0 != act_result.returncode


def test_main_toml_name_has_null(mocker, input_files_path):
    """Verify that the SW triggers an exception when
    the name of the recipe file has a null character"""
    args = MockArgs()
    args.config = f"{input_files_path}/default.config"
    args.recipe_file = f"{input_files_path}/web.xml\0test.toml"
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print = mocker.patch("kit.hekit.print")
    mock_file_exists = mocker.patch("kit.utils.files.file_exists")
    mock_file_exists.return_value = True
    with pytest.raises(SystemExit) as exc_info:
        main()
    mock_print.assert_called_with(
        "Error while running subcommand\n",
        "ValueError('embedded null byte')",
        file=stderr,
    )
    assert 0 != exc_info.value.code


def test_main_toml_wrong_format(tmp_path, hekit_path, input_files_path):
    """Verify that the SW triggers an exception when
    the recipe file contains a float value instead of a string"""
    config_file = create_config_file(tmp_path)
    cmd = f"{hekit_path} --config {config_file} fetch {input_files_path}/test_wrong_format.toml"
    act_result = execute_process(cmd)
    assert "while running subcommand" in act_result.stderr
    assert (
        "TypeError('replace() argument 2 must be str, not float')" in act_result.stderr
    )
    assert 0 != act_result.returncode


def test_main_toml_missing_value(tmp_path, hekit_path, input_files_path):
    """Verify that the SW triggers an exception when
    the recipe file does not have a value in the key=value pair"""
    config_file = create_config_file(tmp_path)
    cmd = f"{hekit_path} --config {config_file} fetch {input_files_path}/test_missing_value.toml"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert (
        "TomlDecodeError('Empty value is invalid (line 7 column 1 char 122)')"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


def test_main_toml_missing_quotes(tmp_path, hekit_path, input_files_path):
    """Verify that the SW triggers an exception when
    the recipe file has a missing quote in key="value" pair"""
    config_file = create_config_file(tmp_path)
    cmd = f"{hekit_path} --config {config_file} fetch {input_files_path}/test_missing_quotes.toml"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert (
        "TomlDecodeError('Unbalanced quotes (line 9 column 24 char 234)')"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self):
        self.version = False
        self.component = "hexl"
        self.instance = "1.2.3"
        self.fn = install_components
        self.upto_stage = "fetch"
        self.force = False
        self.all = False
        self.y = True
        self.recipe_arg = {}
