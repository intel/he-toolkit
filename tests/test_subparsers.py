# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path

from .context import subparsers
from subparsers import files_in_dir, discover_subparsers_from


def test_discover_subparsers_from_commands_all():
    # Arrange
    exp_func = {
        "set_docker_subparser",
        "set_check_dep_subparser",
        "set_install_subparser",
        "set_init_subparser",
        "set_remove_subparser",
        "set_new_subparser",
        "set_list_subparser",
    }
    hekit_root_dir = Path(__file__).resolve().parent.parent

    # Act
    act_funcs = discover_subparsers_from(["commands"], hekit_root_dir / "kit")

    # Assert
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_discover_subparsers_from_commands_some(mocker):
    # Arrange
    exp_func = {"set_check_dep_subparser", "set_remove_subparser", "set_list_subparser"}
    hekit_root_dir = Path(__file__).resolve().parent.parent
    mocker_files_in_dir = mocker.patch("subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["check_deps.py", "remove.py", "list_cmd.py"]

    # Act
    act_funcs = discover_subparsers_from(["commands"], hekit_root_dir / "kit")

    # Assert
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_files_in_dir_commands_filter_py(mocker):
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
    hekit_root_dir = Path(__file__).resolve().parent.parent
    module = hekit_root_dir / "kit" / "commands"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert exp_files == set(filenames)


def test_files_in_dir_commands_filter_None(mocker):
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
    hekit_root_dir = Path(__file__).resolve().parent.parent
    module = hekit_root_dir / "kit" / "commands"
    filter = None

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert exp_files == set(filenames)


def test_discover_subparsers_from_tools_some(mocker):
    # Arrange
    exp_func = {"set_gen_algebras_subparser", "set_gen_primes_subparser"}
    hekit_root_dir = Path(__file__).resolve().parent.parent
    mocker_files_in_dir = mocker.patch("subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["healg.py"]

    # Act
    act_funcs = discover_subparsers_from(["tools"], hekit_root_dir / "kit")

    # Assert
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_files_in_dir_tools_filter_py(mocker):
    # Arrange
    exp_files = {"healg.py"}
    hekit_root_dir = Path(__file__).resolve().parent.parent
    module = hekit_root_dir / "kit" / "tools"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    # Act
    filenames = files_in_dir(module, filter)

    # Assert
    assert exp_files == set(filenames)
