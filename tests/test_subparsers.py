# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path

from .context import subparsers
from subparsers import files_in_dir, discover_subparsers_from


def test_discover_subparsers_from_commands_all():
    # Arrange
    hekit_root_dir = Path(__file__).resolve().parent.parent

    # Act
    func = discover_subparsers_from(["commands"], hekit_root_dir / "kit")

    # Assert
    assert next(func).__name__ == "set_docker_subparser"
    assert next(func).__name__ == "set_check_dep_subparser"
    assert next(func).__name__ == "set_install_subparser"
    assert next(func).__name__ == "set_init_subparser"
    assert next(func).__name__ == "set_remove_subparser"
    assert next(func).__name__ == "set_new_subparser"
    assert next(func).__name__ == "set_list_subparser"


def test_discover_subparsers_from_commands_some(mocker):
    # Arrange
    hekit_root_dir = Path(__file__).resolve().parent.parent
    mocker_files_in_dir = mocker.patch("subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["check_deps.py", "remove.py", "list_cmd.py"]

    # Act
    func = discover_subparsers_from(["commands"], hekit_root_dir / "kit")

    # Assert
    assert next(func).__name__ == "set_check_dep_subparser"
    assert next(func).__name__ == "set_remove_subparser"
    assert next(func).__name__ == "set_list_subparser"


def test_files_in_dir_commands_filter_py(mocker):
    # Arrange
    exp_files = [
        "docker_build.py",
        "check_deps.py",
        "install.py",
        "init.py",
        "remove.py",
        "new.py",
        "list_cmd.py",
    ]
    hekit_root_dir = Path(__file__).resolve().parent.parent
    module = hekit_root_dir / "kit" / "commands"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert filenames == exp_files


def test_files_in_dir_commands_filter_None(mocker):
    # Arrange
    exp_files = [
        "docker_build.py",
        "__init__.py",
        "check_deps.py",
        "install.py",
        "init.py",
        "remove.py",
        "new.py",
        "list_cmd.py",
    ]
    hekit_root_dir = Path(__file__).resolve().parent.parent
    module = hekit_root_dir / "kit" / "commands"
    filter = None

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert filenames == exp_files


def test_discover_subparsers_from_tools_some(mocker):
    # Arrange
    hekit_root_dir = Path(__file__).resolve().parent.parent
    mocker_files_in_dir = mocker.patch("subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["healg.py"]

    # Act
    func = discover_subparsers_from(["tools"], hekit_root_dir / "kit")

    # Assert
    assert next(func).__name__ == "set_gen_algebras_subparser"
    assert next(func).__name__ == "set_gen_primes_subparser"


def test_files_in_dir_tools_filter_py(mocker):
    # Arrange
    exp_files = ["healg.py"]
    hekit_root_dir = Path(__file__).resolve().parent.parent
    module = hekit_root_dir / "kit" / "tools"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert filenames == exp_files
