# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from subprocess import run


def test_cmds_install_list_remove(tmp_path):
    version = "1.2.3"
    config_file, tests_path = create_config_file(tmp_path)

    # Test fetch command
    cmd = [
        "hekit",
        "--config",
        f"{config_file}",
        "fetch",
        f"{tests_path}/input_files/test.toml",
        "--recipe_arg",
        f'"name={version},build=build"',
    ]
    output = execute_process(cmd)
    assert "[GIT] Cloning into 'hexl'..." in output

    # Test list command after fetch
    cmd = ["hekit", "--config", f"{config_file}", "list"]
    output = execute_process(cmd)
    assert f"hexl   {version}   success                         " in output

    # Test build command
    cmd = [
        "hekit",
        "--config",
        f"{config_file}",
        "build",
        f"{tests_path}/input_files/test.toml",
        "--recipe_arg",
        f'"name={version},build=build"',
    ]
    output = execute_process(cmd)
    assert "build" in output

    # Test list command after build
    cmd = ["hekit", "--config", f"{config_file}", "list"]
    output = execute_process(cmd)
    assert f"hexl   {version}   success    success              " in output

    # Test install command
    cmd = [
        "hekit",
        "--config",
        f"{config_file}",
        "install",
        f"{tests_path}/input_files/test.toml",
        "--recipe_arg",
        f'"name={version},build=build"',
    ]
    output = execute_process(cmd)
    assert "install" in output

    # Test list command after isntall
    cmd = ["hekit", "--config", f"{config_file}", "list"]
    output = execute_process(cmd)
    assert f"hexl   {version}   success    success    success   " in output

    # Test remove command
    cmd = ["hekit", "--config", f"{config_file}", "remove", "hexl", f"{version}"]
    output = execute_process(cmd)
    assert f"hexl   {version}   success    success    success   " not in output


"""Utilities used by the tests"""


def create_config_file(path):
    config_file = f"{path}/default.config"
    tests_path = Path(__file__).resolve().parent

    cmd = ["echo", f'repo_location = "{path}"']
    with open(f"{config_file}", "w") as f:
        run(cmd, stdout=f)

    return config_file, tests_path


def execute_process(cmd):
    return run(cmd, capture_output=True).stdout.decode("utf-8")
