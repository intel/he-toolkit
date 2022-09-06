# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest

from pathlib import Path
from kit.utils.subparsers import discover_subparsers_kit, validate_input


def test_discover_subparsers_kit_commands_all(get_toolkit_path):
    exp_func = {
        "set_docker_subparser",
        "set_check_dep_subparser",
        "set_install_subparser",
        "set_init_subparser",
        "set_remove_subparser",
        "set_new_subparser",
        "set_list_subparser",
        "set_plugin_subparser",
    }

    act_funcs = discover_subparsers_kit(["commands"], get_toolkit_path / "kit")
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_discover_subparsers_kit_commands_some(mocker, get_toolkit_path):
    exp_func = {"set_check_dep_subparser", "set_remove_subparser", "set_list_subparser"}
    mocker_files_in_dir = mocker.patch("kit.utils.subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["check_deps.py", "remove.py", "list_cmd.py"]

    act_funcs = discover_subparsers_kit(["commands"], get_toolkit_path / "kit")
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_discover_subparsers_kit_tools_some(mocker, get_toolkit_path):
    exp_func = {"set_gen_algebras_subparser", "set_gen_primes_subparser"}
    mocker_files_in_dir = mocker.patch("kit.utils.subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["healg.py"]

    act_funcs = discover_subparsers_kit(["tools"], get_toolkit_path / "kit")
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_validate_input_non_printable_char():
    input = "test\02file.config"
    with pytest.raises(ValueError) as execinfo:
        validate_input(input)
    assert "Input is not valid due to non-printable characters" == str(execinfo.value)


@pytest.fixture
def get_toolkit_path():
    return Path(__file__).resolve().parent.parent
