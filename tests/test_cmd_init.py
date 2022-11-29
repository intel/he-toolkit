# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from filecmp import cmp as compare_files
from kit.commands.init import (
    create_backup,
    remove_from_rc,
    append_to_rc,
    select_rc_file,
    get_shell_rc_file,
    create_default_config,
    create_plugin_data,
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


def test_select_rc_file_error():
    """Verify that the SW shows an error when the rc file is not found"""
    with pytest.raises(FileNotFoundError) as exc_info:
        act_file = select_rc_file(
            "/mytmp/my_file", "/mylocal/another_file", "/myuser/file_with_data"
        )
    assert (
        str(exc_info.value)
        == f"None of the files '('/mytmp/my_file', '/mylocal/another_file', '/myuser/file_with_data')' exist"
    )


@pytest.mark.parametrize("file_with_data", ["test\n"], indirect=True)
def test_select_rc_file_found(file_with_data):
    """Verify that the SW returns the correct rc file"""
    act_file = select_rc_file("/mytmp/my_file", "/mylocal/another_file", file_with_data)
    assert act_file == file_with_data


def test_get_shell_rc_file_bash(mocker):
    """Verify that the SW returns the correct bash (bash) and rc file"""
    exp_shell, exp_rc_file = "bash", "~/mybashcr"
    mock_exists = mocker.patch.dict(
        "kit.commands.init.environment", {"SHELL": exp_shell}
    )
    mock_select_rc_file = mocker.patch("kit.commands.init.select_rc_file")
    mock_select_rc_file.return_value = exp_rc_file

    act_sell, act_rc_file = get_shell_rc_file()
    assert act_sell == exp_shell
    assert act_rc_file == exp_rc_file


def test_get_shell_rc_file_zsh(mocker):
    """Verify that the SW returns the correct bash (zsh) and rc file"""
    exp_shell, exp_rc_file = "zsh", "~/anotherbashcr"
    mock_exists = mocker.patch.dict(
        "kit.commands.init.environment", {"SHELL": exp_shell}
    )
    mock_select_rc_file = mocker.patch("kit.commands.init.select_rc_file")
    mock_select_rc_file.return_value = exp_rc_file

    act_sell, act_rc_file = get_shell_rc_file()
    assert act_sell == exp_shell
    assert act_rc_file == exp_rc_file


def test_get_shell_rc_file_unknown_shell(mocker):
    """Verify that the SW shows an error when the shell is unknown"""
    exp_shell, exp_rc_file = "unknownshell", "~/itsbashcr"
    mock_exists = mocker.patch.dict(
        "kit.commands.init.environment", {"SHELL": exp_shell}
    )
    mock_select_rc_file = mocker.patch("kit.commands.init.select_rc_file")
    mock_select_rc_file.return_value = exp_rc_file

    with pytest.raises(ValueError) as exc_info:
        act_sell, act_rc_file = get_shell_rc_file()
    assert str(exc_info.value) == f"Unknown shell '{exp_shell}'"


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
