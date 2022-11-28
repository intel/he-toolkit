# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from filecmp import cmp as compare_files
from kit.commands.init import (
    create_backup,
    remove_from_rc,
    append_to_rc,
    # select_rc_file
    # get_shell_rc_file
    create_default_config,
    create_plugin_data,
    # get_rc_new_lines
)


@pytest.mark.parametrize(
    "file_with_data", ["The cat\nsat on\nthe mat\n"], indirect=True
)
def test_create_backup(file_with_data):
    """Verify that the SW makes a backup of the rc file"""
    rc_path = file_with_data
    backup = create_backup(rc_path)

    assert file_not_empty(file_with_data)
    assert file_not_empty(backup)
    assert compare_files(file_with_data, backup)


@pytest.mark.parametrize(
    "file_with_data",
    [
        (
            "ipsum\n"
            "\n"
            "# >>> hekit start >>>\n"
            "a\n"
            "b\n"
            "c\n"
            "# <<<  hekit end  <<<\n"
            "\n"
            "lorum\n"
        )
    ],
    indirect=True,
)
def test_remove_from_rc(file_with_data):
    """Verify that the SW removes the lines related to toolkit usage from the rc file"""
    rc_path = file_with_data
    remove_from_rc(rc_path)
    assert rc_path.read_text() == "ipsum\n\n\nlorum\n"


@pytest.mark.parametrize("file_with_data", ["the beginning\n"], indirect=True)
def test_append_to_rc(file_with_data):
    """Verify that the SW appends the lines related to toolkit usage in the rc file"""
    rc_path = file_with_data
    append_to_rc(rc_path, content="the contents")
    with rc_path.open() as f:
        lines = f.readlines()

    assert lines == [
        "the beginning\n",
        "\n",
        "the contents\n",
        "\n",
    ]


def test_append_to_rc_when_file_does_not_exist():
    """Verify that the SW shows an error when trying yo append the
    lines related to toolkit usage but rc file does not exist"""
    with pytest.raises(FileNotFoundError) as execinfo:
        rc_path = Path("/test/notlikelyfile.txt")
        append_to_rc(rc_path, content="")


@pytest.mark.parametrize("create_config", ["default.config"], indirect=True)
def test_create_default_config_file_exist(create_config, mocker):
    """Verify that the SW print an error message when
    the default config file exists"""
    exp_file = "default.config"
    mock_print = mocker.patch("kit.commands.init.print")
    create_default_config(create_config)
    assert file_not_empty(create_config / exp_file)
    mock_print.assert_any_call(f"{create_config}/{exp_file} file already exists")


def test_create_default_config_file_created(mocker, tmp_path):
    """Verify that the SW creates a default config file"""
    exp_file = "default.config"
    mock_print = mocker.patch("kit.commands.init.print")
    create_default_config(tmp_path)
    assert file_not_empty(tmp_path / exp_file)
    mock_print.assert_any_call(f"{tmp_path}/{exp_file} created")


@pytest.mark.parametrize("create_plugin", ["plugins.toml"], indirect=True)
def test_create_plugin_data_file_exists(create_plugin, mocker):
    """Verify that the SW print an error message when
    the default plugin data exists"""
    exp_file = "plugins/plugins.toml"
    mock_print = mocker.patch("kit.commands.init.print")
    create_plugin_data(create_plugin)
    assert file_not_empty(create_plugin / exp_file)
    mock_print.assert_any_call(f"{create_plugin}/{exp_file} file already exists")


def test_create_plugin_data_file_created(mocker, tmp_path):
    """Verify that the SW creates the default plugin data"""
    exp_file = "plugins/plugins.toml"
    mock_print = mocker.patch("kit.commands.init.print")
    create_plugin_data(tmp_path)
    assert file_not_empty(tmp_path / exp_file)
    mock_print.assert_any_call(f"{tmp_path}/{exp_file} created")


"""Utilities used by the tests"""


def file_not_empty(path: str) -> bool:
    """Helper"""
    return Path(path).stat().st_size > 0


@pytest.fixture
def file_with_data(tmp_path, request) -> Path:
    path = tmp_path / "test.txt"
    path.write_text(request.param)
    return path.expanduser().resolve()


@pytest.fixture
def create_config(tmp_path, request):
    path = tmp_path / request.param
    path.write_text("test\n")
    return tmp_path


@pytest.fixture
def create_plugin(tmp_path, request):
    plugins_path = tmp_path / "plugins"
    plugins_path.mkdir(exist_ok=True)
    plugins_file = plugins_path / request.param
    plugins_file.write_text("test\n")
    return tmp_path
