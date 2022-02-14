# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from filecmp import cmp as compare_files
from kit.command_init import create_backup, remove_from_rc, append_to_rc


def file_not_empty(path: str) -> bool:
    """Helper"""
    return Path(path).stat().st_size > 0


def test_create_backup(file_with_some_data):
    """"""
    backup = create_backup(file_with_some_data)

    assert file_not_empty(file_with_some_data)
    assert file_not_empty(backup)
    assert compare_files(file_with_some_data, backup)


def test_remove_from_rc():
    """"""
    assert False


def test_append_to_rc():
    """"""
    assert False


@pytest.fixture
def file_with_some_data(tmp_path: Path) -> Path:
    path = tmp_path / "test.txt"
    path.write_text("The cat\nsat on\nthe mat\n")
    return path
