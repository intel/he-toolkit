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


def test_get_instances_two_instances(mocker, tmp_path):
    """Verify that the SW returns the lists of a component with two instances"""
    args = Mockargs()
    exp_comp = "hexl"
    exp_inst = ["1.0.1", "1.2.3"]
    mock_load_config = mocker.patch("kit.utils.tab_completion.load_config")
    mock_load_config.return_value = Config(tmp_path)
    create_plugin_file(tmp_path, exp_comp, exp_inst)

    act_comp = components_completer("", args)
    act_inst = instances_completer("", args)
    assert act_comp == [exp_comp]
    assert act_inst == exp_inst


def test_get_instances_one_instance(mocker, tmp_path):
    """Verify that the SW returns the lists of a component with one instance"""
    args = Mockargs()
    exp_comp = "hexl"
    exp_inst = ["1.2.3"]
    mock_load_config = mocker.patch("kit.utils.tab_completion.load_config")
    mock_load_config.return_value = Config(tmp_path)
    create_plugin_file(tmp_path, exp_comp, exp_inst)

    act_comp = components_completer("", args)
    act_inst = instances_completer("", args)
    assert act_comp == [exp_comp]
    assert act_inst == exp_inst


def test_get_instances_empty(mocker, tmp_path):
    """Verify that the SW returns an empty lists when there is no components"""
    args = Mockargs()
    mock_load_config = mocker.patch("kit.utils.tab_completion.load_config")
    mock_load_config.return_value = Config(tmp_path)

    act_comp = components_completer("", args)
    act_inst = instances_completer("", args)
    assert act_comp == []
    assert act_inst == []


def test_get_plugins_by_state_enable(create_tmp_file):
    """Verify that the SW returns the enabled plugins"""
    act_data = get_plugins_by_state(PluginState.ENABLE, create_tmp_file)
    assert "plugin_a" in act_data
    assert "plugin_c" not in act_data
    assert "plugin_e" not in act_data


def test_get_plugins_by_state_disable(create_tmp_file):
    """Verify that the SW returns the disabled plugins"""
    act_data = get_plugins_by_state(PluginState.DISABLE, create_tmp_file)
    assert "plugin_c" in act_data
    assert "plugin_a" not in act_data
    assert "plugin_e" not in act_data


"""Utilities used by the tests"""


class Config:
    def __init__(self, repo_location):
        self.repo_location = repo_location


class Mockargs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.component = "hexl"
        self.config = f"{self.tests_path}/input_files/default.config"


def create_plugin_file(tmp_path, component, instances):
    component_path = tmp_path / component
    component_path.mkdir(exist_ok=True)

    for instance in instances:
        instance_path = component_path / instance
        instance_path.mkdir(exist_ok=True)


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
