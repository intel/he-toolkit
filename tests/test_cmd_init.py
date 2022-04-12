# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from filecmp import cmp as compare_files
from .context import command_init
from command_init import (
    create_backup,
    remove_from_rc,
    append_to_rc,
    get_expanded_path,
    create_default_config,
)


def file_not_empty(path: str) -> bool:
    """Helper"""
    return Path(path).stat().st_size > 0


@pytest.mark.parametrize(
    "file_with_data", ["The cat\nsat on\nthe mat\n"], indirect=True
)
def test_create_backup(file_with_data):
    """"""
    rc_path = get_expanded_path(file_with_data)
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
    """"""
    rc_path = get_expanded_path(file_with_data)
    remove_from_rc(rc_path)
    assert rc_path.read_text() == "ipsum\n\n\nlorum\n"


@pytest.mark.parametrize("file_with_data", ["the beginning\n"], indirect=True)
def test_append_to_rc(file_with_data):
    """"""
    rc_path = get_expanded_path(file_with_data)
    append_to_rc(rc_path, content="the contents")
    with rc_path.open() as f:
        lines = f.readlines()

    assert lines == [
        "the beginning\n",
        "\n",
        "# >>> hekit start >>>\n",
        "the contents\n",
        "# <<<  hekit end  <<<\n",
        "\n",
    ]


def test_append_to_rc_when_file_does_not_exist():
    """"""
    with pytest.raises(FileNotFoundError) as execinfo:
        rc_path = get_expanded_path("notlikelyfile.txt")
        append_to_rc(rc_path, content="")


def test_create_default_config_file_exist(mocker):
    """Arrange"""
    mock_exists = mocker.patch("command_init.file_exists")
    mock_exists.return_value = True
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    mock_open = mocker.patch.object(Path, "open")
    mock_print = mocker.patch("command_init.print")

    """Act"""
    create_default_config()

    """Assert"""
    mock_mkdir.assert_called_once()
    mock_open.assert_not_called()
    mock_print.assert_any_call("~/.hekit/default.config file already exists")


def test_create_default_config_file_created(mocker):
    """Arrange"""
    mock_exists = mocker.patch("command_init.file_exists")
    mock_exists.return_value = False
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    mock_open = mocker.patch.object(Path, "open")
    mock_print = mocker.patch("command_init.print")

    """Act"""
    create_default_config()

    """Assert"""
    mock_mkdir.assert_called_once()
    mock_open.assert_called_once()
    mock_print.assert_any_call("~/.hekit/default.config created")


@pytest.fixture
def file_with_data(tmp_path, request) -> Path:
    path = tmp_path / "test.txt"
    path.write_text(request.param)
    return path
