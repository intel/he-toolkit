# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from tests.common_utils import (
    create_config_file,
    execute_process,
    hekit_path,
    input_files_path,
)


def test_cmds_install_list_remove(tmp_path, hekit_path, input_files_path):
    """Verify that fetch, build, install, list and remove commands
    are executed without failures"""
    component, instance = "hexl", "1.2.3"
    config_file = create_config_file(tmp_path)

    # Test fetch command
    cmd = f"{hekit_path} --config {config_file} fetch {input_files_path}/test.toml"
    act_result = execute_process(cmd)
    assert f"fetch" in act_result.stdout
    assert not act_result.stderr
    assert 0 == act_result.returncode

    # Test list command after fetch
    cmd = f"{hekit_path} --config {config_file} list"
    act_result = execute_process(cmd)
    assert (
        f"{component}        {instance}      success                        "
        in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode

    # Test build command
    cmd = f"{hekit_path} --config {config_file} build {input_files_path}/test.toml"
    act_result = execute_process(cmd)
    assert "build" in act_result.stdout
    assert not act_result.stderr
    assert 0 == act_result.returncode

    # Test list command after build
    cmd = f"{hekit_path} --config {config_file} list"
    act_result = execute_process(cmd)
    assert (
        f"{component}        {instance}      success    success              "
        in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode

    # Test install command
    cmd = f"{hekit_path} --config {config_file} install {input_files_path}/test.toml"
    act_result = execute_process(cmd)
    assert "install" in act_result.stdout
    assert not act_result.stderr
    assert 0 == act_result.returncode

    # Test list command after install
    cmd = f"{hekit_path} --config {config_file} list"
    act_result = execute_process(cmd)
    assert (
        f"{component}        {instance}      success    success    success   "
        in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode

    # Test remove command
    cmd = f"{hekit_path} --config {config_file} remove {component} {instance}"
    act_result = execute_process(cmd)
    assert (
        f"{component}   {instance}   success    success    success   "
        not in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode
