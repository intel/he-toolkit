# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest

from pathlib import Path
from kit.utils.constants import PluginsConfig
from kit.utils.subparsers import (
    discover_subparsers_kit,
    discover_subparsers_plugins,
    validate_input,
)


def test_discover_subparsers_plugins_tmp_file(mocker, tmp_path):
    """Verify that the SW reads the files defined in start
    and returns the function that defines the arguments"""
    start_files, modules = create_plugin_file(tmp_path)
    exp_func = {f"set_{modules[0]}_subparser", f"set_{modules[1]}_subparser"}
    mocker_files_in_dir = mocker.patch("kit.utils.subparsers.load_toml")
    mocker_files_in_dir.return_value = {
        PluginsConfig.KEY: {
            modules[0]: {"start": start_files[0]},
            modules[1]: {"start": start_files[1]},
        }
    }

    act_funcs = discover_subparsers_plugins(modules, tmp_path)
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_discover_subparsers_kit_commands_all(get_toolkit_path):
    """Verify that the SW reads all the files in commands directory
    and returns the functions that define the arguments"""
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
    """Verify that the SW reads some files in commands directory
    and returns the functions that define the arguments"""
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
    """Verify that the SW reads all the files in tools directory
    and returns the functions that define the arguments"""
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
    """Verify that the SW raises an error when
    there is a non printable char"""
    input = "test\02file.config"
    with pytest.raises(ValueError) as execinfo:
        validate_input(input)
    assert "Input is not valid due to non-printable characters" == str(execinfo.value)


"""Utilities used by the tests"""


@pytest.fixture
def get_toolkit_path():
    return Path(__file__).resolve().parent.parent


def create_plugin_file(tmp_path):
    modules = ["plugin_a", "plugin_b"]
    start_files = ["test_a.py", "test_b.py"]
    for module, start_file in zip(modules, start_files):
        plugin_path = tmp_path / module
        plugin_path.mkdir(exist_ok=True)

        input_file = plugin_path / start_file
        with input_file.open("w") as f:
            f.write(f"def set_{module}_subparser(subparsers):\n" "    pass\n")

    return start_files, modules
