# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from os import getcwd, chdir

from .context import hekit, tab_completion, command_remove, command_install
from hekit import main
from tab_completion import components_completer, instances_completer
from command_remove import remove_components
from command_install import install_components


# Due to install command changes current directory,
# the other commands need to restore the current path
cwd_test = getcwd()


def execute_action(mocker, args_action):
    global cwd_test
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_action, ""
    main()
    chdir(cwd_test)


def test_get_instances_after_fetch(mocker, args_fetch, args_tab, comp_data):
    """Arrange"""
    execute_action(mocker, args_fetch)
    exp_comp = [comp_data["comp"]]
    exp_inst = [comp_data["inst_v1"], comp_data["inst_v2"]]

    """Act"""
    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)

    """Assert"""
    assert act_comp == exp_comp
    assert act_inst == exp_inst


def test_get_instances_after_remove_v1(mocker, args_remove_v1, args_tab, comp_data):
    """Arrange"""
    execute_action(mocker, args_remove_v1)
    exp_comp = [comp_data["comp"]]
    exp_inst = [comp_data["inst_v2"]]

    """Act"""
    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)

    """Assert"""
    assert act_comp == exp_comp
    assert act_inst == exp_inst


def test_get_instances_after_remove_v2(mocker, args_remove_v2, args_tab):
    """Arrange"""
    execute_action(mocker, args_remove_v2)
    exp_comp = []
    exp_inst = []

    """Act"""
    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)

    """Assert"""
    assert act_comp == exp_comp
    assert act_inst == exp_inst


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, fn, component, instance, upto_stage):
        self.version = False
        self.component = component
        self.instance = instance
        self.config = "tests/config/default.config"
        self.recipe_file = "tests/config/test_two_instances.toml"
        self.fn = fn
        self.upto_stage = upto_stage
        self.recipe_arg = None


@pytest.fixture
def comp_data():
    return {"comp": "hexl", "inst_v1": "1.2.2", "inst_v2": "1.2.3"}


@pytest.fixture
def args_tab(comp_data):
    return MockArgs(None, comp_data["comp"], "", "")


@pytest.fixture
def args_fetch(comp_data):
    return MockArgs(install_components, "", "", "fetch")


@pytest.fixture
def args_remove_v1(comp_data):
    return MockArgs(remove_components, comp_data["comp"], comp_data["inst_v1"], "")


@pytest.fixture
def args_remove_v2(comp_data):
    return MockArgs(remove_components, comp_data["comp"], comp_data["inst_v2"], "")
