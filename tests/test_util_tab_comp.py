# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from toml import dump
from pathlib import Path
from kit.utils.constants import PluginState, PluginsConfig
from kit.utils.tab_completion import (
    get_plugins_by_state,
    components_completer,
    instances_completer,
)


def test_get_instances_two_instances(mocker, args_tab, comp_data):
    exp_comp = [comp_data["comp"]]
    exp_inst = [comp_data["inst_v1"], comp_data["inst_v2"]]
    mock_list_dirs = mocker.patch("kit.utils.tab_completion.list_dirs")
    mock_list_dirs.side_effect = [exp_comp, exp_inst]

    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)
    assert act_comp == exp_comp
    assert act_inst == exp_inst


def test_get_instances_after_remove_v1(mocker, args_tab, comp_data):
    exp_comp = [comp_data["comp"]]
    exp_inst = [comp_data["inst_v2"]]
    mock_list_dirs = mocker.patch("kit.utils.tab_completion.list_dirs")
    mock_list_dirs.side_effect = [exp_comp, exp_inst]

    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)
    assert act_comp == exp_comp
    assert act_inst == exp_inst


def test_get_instances_after_remove_v2(mocker, args_tab):
    exp_comp = []
    exp_inst = []
    mock_list_dirs = mocker.patch("kit.utils.tab_completion.list_dirs")
    mock_list_dirs.side_effect = [exp_comp, exp_inst]

    act_comp = components_completer("", args_tab)
    act_inst = instances_completer("", args_tab)
    assert act_comp == exp_comp
    assert act_inst == exp_inst


def test_get_plugins_by_state_enable(create_tmp_file):
    act_data = get_plugins_by_state(PluginState.ENABLE, create_tmp_file)
    assert "plugin_a" in act_data
    assert "plugin_c" not in act_data
    assert "plugin_e" not in act_data


def test_get_plugins_by_state_disable(create_tmp_file):
    act_data = get_plugins_by_state(PluginState.DISABLE, create_tmp_file)
    assert "plugin_c" in act_data
    assert "plugin_a" not in act_data
    assert "plugin_e" not in act_data


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


@pytest.fixture
def create_tmp_file(tmp_path):
    file_name = tmp_path / "test.toml"
    file_data = {
        PluginsConfig.KEY: {
            "plugin_a": {"version": "1.0.0", "state": PluginState.ENABLE},
            "plugin_c": {"version": "1.0.0", "state": PluginState.DISABLE},
            "plugin_e": {"version": "1.0.0", "state": "g"},
        }
    }

    with file_name.open("w", encoding="utf-8") as f:
        dump(file_data, f)

    return file_name
