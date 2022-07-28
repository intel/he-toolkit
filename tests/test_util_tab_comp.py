# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from os import getcwd, chdir
from pathlib import Path
from kit.utils.tab_completion import components_completer, instances_completer


def test_get_instances_after_fetch(mocker, args_tab, comp_data):
    """Arrange"""
    exp_comp = [comp_data["comp"]]
    exp_inst = [comp_data["inst_v1"], comp_data["inst_v2"]]
    mock_list_dirs = mocker.patch("kit.utils.tab_completion.list_dirs")
    mock_list_dirs.side_effect = [exp_comp, exp_inst]

    """Act"""
    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)

    """Assert"""
    assert act_comp == exp_comp
    assert act_inst == exp_inst


def test_get_instances_after_remove_v1(mocker, args_tab, comp_data):
    """Arrange"""
    exp_comp = [comp_data["comp"]]
    exp_inst = [comp_data["inst_v2"]]
    mock_list_dirs = mocker.patch("kit.utils.tab_completion.list_dirs")
    mock_list_dirs.side_effect = [exp_comp, exp_inst]

    """Act"""
    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)

    """Assert"""
    assert act_comp == exp_comp
    assert act_inst == exp_inst


def test_get_instances_after_remove_v2(mocker, args_tab):
    """Arrange"""
    exp_comp = []
    exp_inst = []
    mock_list_dirs = mocker.patch("kit.utils.tab_completion.list_dirs")
    mock_list_dirs.side_effect = [exp_comp, exp_inst]

    """Act"""
    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)

    """Assert"""
    assert act_comp == exp_comp
    assert act_inst == exp_inst


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, fn, component, instance, upto_stage):
        self.tests_path = Path(__file__).resolve().parent
        self.version = False
        self.component = component
        self.instance = instance
        self.config = f"{self.tests_path}/input_files/default.config"
        self.recipe_file = f"{self.tests_path}/input_files/test.toml"
        self.fn = fn
        self.upto_stage = upto_stage
        self.force = False
        self.all = False
        self.y = True
        self.recipe_arg = {}


@pytest.fixture
def comp_data():
    return {"comp": "hexl", "inst_v1": "1.2.2", "inst_v2": "1.2.3"}


@pytest.fixture
def args_tab(comp_data):
    return MockArgs(None, comp_data["comp"], instance="", upto_stage="")
