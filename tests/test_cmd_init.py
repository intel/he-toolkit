# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from filecmp import cmp as compare_files
from kit.command_init import (
    create_backup,
    remove_from_bash_profile,
    write_to_bash_profile,
)


def test_create_backup(file_with_some_data):
    """"""
    create_backup()

    assert file_not_empty()
    assert file_not_empty()
    assert compare_files(file_with_some_data, backup_file)


@pytest
def file_with_some_data(tmp_path):
    path = tmp_path / "test.txt"
    with path.open() as f:
        f.write("The cat\n" "sat on\n" "the mat\n")
    return path
