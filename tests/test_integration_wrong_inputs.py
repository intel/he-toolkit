# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from unittest import skip
import pytest
from tests.common_utils import create_config_file, execute_process, get_tests_path


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
    cmd = f"hekit --config fetch{tests_path}/input_files/web.xml\0default.config list"

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
def test_main_toml_name_has_null():
    # Arrange

    tests_path = get_tests_path()
    cmd = f"hekit --config {args_fetch.tests_path}/input_files/web.xml\0test.toml"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "embedded null byte" in err
    assert "Error while running subcommand" in err


def test_main_toml_wrong_format(tmp_path):
    """Verify that the SW will trigger an exception when
    the config file is a wrong format"""
    # Arrange
    config_file = create_config_file(tmp_path)
    tests_path = get_tests_path()
    cmd = f"hekit --config {config_file} fetch {tests_path}/input_files/test_wrong_format.toml"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "while running subcommand" in err
    assert "TypeError('replace() argument 2 must be str, not float')" in err


def test_main_toml_missing_value(tmp_path):
    """Verify that the SW will trigger an exception when
    the config file is missing values or empty value or invalid"""
    # Arrange
    config_file = create_config_file(tmp_path)
    tests_path = get_tests_path()
    cmd = f"hekit --config {config_file} fetch {tests_path}/input_files/test_missing_value.toml"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "TomlDecodeError('Empty value is invalid (line 7 column 1 char 122)')" in err
    assert "Error while running subcommand" in err


def test_main_toml_missing_quotes(tmp_path):
    """Verify that the SW will trigger an exception when
    the config file is a missing quotes"""
    # Arrange
    config_file = create_config_file(tmp_path)
    tests_path = get_tests_path()
    cmd = f"hekit --config {config_file} fetch {tests_path}/input_files/test_missing_quotes.toml"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "TomlDecodeError('Unbalanced quotes (line 9 column 24 char 234)')" in err
    assert "Error while running subcommand" in err
