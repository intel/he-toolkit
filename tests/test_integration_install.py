# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from tests.common_utils import create_config_file, execute_process, get_tests_path


def test_cmds_install_list_remove(tmp_path):
    """Verify that fetch, build, install, list and remove commands
    are executed without failures"""
    component, instance = "hexl", "1.2.3"
    config_file = create_config_file(tmp_path)
    tests_path = get_tests_path()

    # Test fetch command
    cmd = [
        "hekit",
        "--config",
        f"{config_file}",
        "fetch",
        f"{tests_path}/input_files/test.toml",
    ]
    output = execute_process(cmd)
    assert f"fetch" in output

    # Test list command after fetch
    cmd = ["hekit", "--config", f"{config_file}", "list"]
    output = execute_process(cmd)
    assert f"{component}   {instance}   success                         " in output

    # Test build command
    cmd = [
        "hekit",
        "--config",
        f"{config_file}",
        "build",
        f"{tests_path}/input_files/test.toml",
    ]
    output = execute_process(cmd)
    assert "build" in output

    # Test list command after build
    cmd = ["hekit", "--config", f"{config_file}", "list"]
    output = execute_process(cmd)
    assert f"{component}   {instance}   success    success              " in output

    # Test install command
    cmd = [
        "hekit",
        "--config",
        f"{config_file}",
        "install",
        f"{tests_path}/input_files/test.toml",
    ]
    output = execute_process(cmd)
    assert "install" in output

    # Test list command after isntall
    cmd = ["hekit", "--config", f"{config_file}", "list"]
    output = execute_process(cmd)
    assert f"{component}   {instance}   success    success    success   " in output

    # Test remove command
    cmd = [
        "hekit",
        "--config",
        f"{config_file}",
        "remove",
        f"{component}",
        f"{instance}",
    ]
    output = execute_process(cmd)
    assert f"{component}   {instance}   success    success    success   " not in output
