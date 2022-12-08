# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest

from pathlib import Path
from kit.utils.constants import PluginsConfig
from kit.utils.subparsers import (
    get_subparsers_plugins,
    get_plugin_arg_choices,
    get_plugins_start_files,
    get_subparsers_kit,
    validate_input,
)


def test_get_subparsers_plugins_tmp_file(mocker, tmp_path):
    """Verify that the SW reads the files defined in start
    and returns the function that defines the arguments"""
    modules = ["test", "plugin"]
    exp_func = {f"set_{modules[0]}_subparser", f"set_{modules[1]}_subparser"}
    plugin_config = {
        modules[0]: f"start_{modules[0]}.py",
        modules[1]: f"start_{modules[1]}.py",
    }
    create_plugin(modules, tmp_path)

    act_funcs = get_subparsers_plugins(plugin_config, tmp_path)
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_get_plugin_arg_choices(tmp_path):
    """Verify that the SW returns the argument name"""
    plugin_name = "test"
    create_plugin([plugin_name], tmp_path)

    act_choice = get_plugin_arg_choices(plugin_name, tmp_path)
    assert len(act_choice) == 1
    assert act_choice[0] == f"prog_{plugin_name}"


def test_get_plugins_start_files(tmp_path):
    plugin_name = "test"
    create_plugin_config(plugin_name, tmp_path)

    act_dict = get_plugins_start_files(tmp_path / plugin_name / "plugin.toml")
    assert act_dict[plugin_name] == f"start_{plugin_name}.py"


def test_get_subparsers_kit_commands_all(get_toolkit_path):
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

    act_funcs = get_subparsers_kit(["commands"], get_toolkit_path / "kit")
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_get_subparsers_kit_commands_some(mocker, get_toolkit_path):
    """Verify that the SW reads some files in commands directory
    and returns the functions that define the arguments"""
    exp_func = {"set_check_dep_subparser", "set_remove_subparser", "set_list_subparser"}
    mocker_files_in_dir = mocker.patch("kit.utils.subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["check_deps.py", "remove.py", "list_cmd.py"]

    act_funcs = get_subparsers_kit(["commands"], get_toolkit_path / "kit")
    for func in act_funcs:
        func_name = func.__name__
        assert func_name in exp_func
        exp_func.remove(func_name)
    assert 0 == len(exp_func)


def test_get_subparsers_kit_tools_some(mocker, get_toolkit_path):
    """Verify that the SW reads all the files in tools directory
    and returns the functions that define the arguments"""
    exp_func = {"set_gen_algebras_subparser", "set_gen_primes_subparser"}
    mocker_files_in_dir = mocker.patch("kit.utils.subparsers.files_in_dir")
    mocker_files_in_dir.return_value = ["algebras.py", "gen_primes.py"]

    act_funcs = get_subparsers_kit(["tools"], get_toolkit_path / "kit")
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


def create_plugin(modules, tmp_path):
    for module in modules:
        plugin_path = tmp_path / module
        plugin_path.mkdir(exist_ok=True)

        toml_file = plugin_path / "plugin.toml"
        with toml_file.open("w") as f:
            f.write(
                "[plugin]\n"
                f'name = "{module}"\n'
                'version = "1.1.0"\n'
                f'start = "start_{module}.py"\n'
            )

        start_file = plugin_path / f"start_{module}.py"
        with start_file.open("w") as f:
            f.write(
                "def test_func(args):\n"
                "   pass\n\n"
                f"def set_{module}_subparser(subparsers):\n"
                f"   parser_{module} = subparsers.add_parser('prog_{module}')\n"
                f"   parser_{module}.set_defaults(fn=test_func)\n"
            )


def create_plugin_config(plugin_name, tmp_path):
    plugin_path = tmp_path / plugin_name
    plugin_path.mkdir(exist_ok=True)

    toml_file = plugin_path / "plugin.toml"
    with toml_file.open("w") as f:
        f.write(
            f"[plugins.{plugin_name}]\n"
            'version = "1.1.0"\n'
            f'start = "start_{plugin_name}.py"\n'
            'state = "enabled"\n'
        )
