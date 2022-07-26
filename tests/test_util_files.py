# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest

from pathlib import Path
from kit.utils.files import files_in_dir, list_dirs


def test_files_in_dir_commands_filter_py(get_toolkit_path):
    # Arrange
    exp_files = {
        "docker_build.py",
        "check_deps.py",
        "install.py",
        "init.py",
        "remove.py",
        "new.py",
        "list_cmd.py",
    }
    module = get_toolkit_path / "kit" / "commands"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert exp_files == set(filenames)


def test_files_in_dir_commands_filter_None(get_toolkit_path):
    # Arrange
    exp_files = {
        "docker_build.py",
        "__init__.py",
        "check_deps.py",
        "install.py",
        "init.py",
        "remove.py",
        "new.py",
        "list_cmd.py",
    }
    module = get_toolkit_path / "kit" / "commands"
    filter = None

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert exp_files == set(filenames)


def test_files_in_dir_tools_filter_py(get_toolkit_path):
    # Arrange
    exp_files = {"healg.py"}
    module = get_toolkit_path / "kit" / "tools"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert exp_files == set(filenames)


def test_list_dirs(get_toolkit_path):
    # Arrange
    exp_files = ["utils", "tools", "commands"]
    module = get_toolkit_path / "kit"

    # Act
    directories = list_dirs(module)

    # Assert
    assert exp_files[0] in set(directories)
    assert exp_files[1] in set(directories)
    assert exp_files[2] in set(directories)


@pytest.fixture
def get_toolkit_path():
    return Path(__file__).resolve().parent.parent
