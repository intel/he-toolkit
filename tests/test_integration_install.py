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
    cmd = f"hekit --config {config_file} fetch {tests_path}/input_files/test.toml"
    out, err = execute_process(cmd)
    assert f"fetch" in out
    assert not err

    # Test list command after fetch
    cmd = f"hekit --config {config_file} list"
    out, err = execute_process(cmd)
    assert f"{component}   {instance}   success                         " in out
    assert not err

    # Test build command
    cmd = f"hekit --config {config_file} build {tests_path}/input_files/test.toml"
    out, err = execute_process(cmd)
    assert "build" in out
    assert not err

    # Test list command after build
    cmd = f"hekit --config {config_file} list"
    out, err = execute_process(cmd)
    assert f"{component}   {instance}   success    success              " in out
    assert not err

    # Test install command
    cmd = f"hekit --config {config_file} install {tests_path}/input_files/test.toml"
    out, err = execute_process(cmd)
    assert "install" in out
    assert not err

    # Test list command after isntall
    cmd = f"hekit --config {config_file} list"
    out, err = execute_process(cmd)
    assert f"{component}   {instance}   success    success    success   " in out
    assert not err

    # Test remove command
    cmd = f"hekit --config {config_file} remove {component} {instance}"
    out, err = execute_process(cmd)
    assert f"{component}   {instance}   success    success    success   " not in out
    assert not err
