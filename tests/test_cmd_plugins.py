# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from shutil import make_archive
from pathlib import Path
from kit.utils.constants import PluginsConfig, PluginState
from kit.commands.plugin import (
    PluginType,
    list_plugins,
    update_plugin_state,
    get_plugin_type,
    check_plugin_structure,
)


def test_get_plugin_type_all_valid(tmp_path):
    """Verify the function returns the correct plugin type"""
    plugin_name = "MyPlugin"
    create_plugins_files(plugin_name, tmp_path)

    assert PluginType.DIR == get_plugin_type(tmp_path / plugin_name)
    assert PluginType.TAR == get_plugin_type(tmp_path / f"{plugin_name}.tar.gz")
    assert PluginType.TAR == get_plugin_type(tmp_path / f"{plugin_name}.tar.xz")
    assert PluginType.TAR == get_plugin_type(tmp_path / f"{plugin_name}.tar.bz2")
    assert PluginType.ZIP == get_plugin_type(tmp_path / f"{plugin_name}.zip")


def test_get_plugin_type_not_found():
    """Verify the function raises an error
    when the file is not found"""
    plugin_name = "MyPlugin"
    with pytest.raises(FileNotFoundError) as exc_info:
        get_plugin_type(Path(plugin_name))
    assert str(exc_info.value) == f"File '{plugin_name}' not found"


def test_get_plugin_type_not_supported():
    """Verify the function raises an error
    when the file does not exist"""
    tests_path = Path(__file__).resolve().parent
    file = tests_path / "input_files/default.config"
    with pytest.raises(TypeError) as exc_info:
        get_plugin_type(file)
    assert str(exc_info.value) == "This program only supports tarball or zip files"


def test_list_plugins_all(mocker):
    """Verify the function prints all plugins"""
    args = MockArgs()
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 3 == mockers.mock_print.call_count
    mockers.mock_print.assert_any_call("plugin2    disabled  ")
    mockers.mock_print.assert_any_call("plugin1    enabled   ")


def test_list_plugins_enable(mocker):
    """Verify the function prints only enabled plugins"""
    args = MockArgs()
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with("plugin1    enabled   ")


def test_list_plugins_disable(mocker):
    """Verify the function prints only disabled plugins"""
    args = MockArgs()
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with("plugin2    disabled  ")


def test_update_plugin_state_unknown_plugin(mocker):
    """Verify the function reports a message
    when the plugin is not in the system"""
    args = MockArgs()
    args.plugin = "test"
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with("Plugin test was not found in the system")


def test_update_plugin_state_already_enabled(mocker):
    """Verify the function reports a message
    when the plugin is already enabled"""
    args = MockArgs()
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with(
        "Plugin plugin1 is already enabled in the system"
    )


def test_update_plugin_state_already_disabled(mocker):
    """Verify the function reports a message
    when the plugin is already disabled"""
    args = MockArgs()
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with(
        "Plugin plugin1 is already enabled in the system"
    )


def test_update_plugin_state_enable(mocker):
    """Verify the function enables a plugin"""
    args = MockArgs()
    args.plugin = "plugin2"
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with("Plugin plugin2 was enabled successfully")


def test_update_plugin_state_disable(mocker):
    """Verify the function disables a plugin"""
    args = MockArgs()
    args.plugin = "plugin1"
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with("Plugin plugin1 was disabled successfully")


"""Utilities used by the tests"""


def geet_fake_dict():
    return {"plugin1": PluginState.ENABLE, "plugin2": PluginState.DISABLE}


def create_plugins_files(plugin_name, tmp_path, type="all"):
    plugin = tmp_path / plugin_name
    plugin.mkdir(exist_ok=True)

    if type in ["all", "tar"]:
        make_archive(plugin, "gztar", tmp_path)
        make_archive(plugin, "bztar", tmp_path)
        make_archive(plugin, "xztar", tmp_path)

    if type in ["all", "zip"]:
        make_archive(plugin, "zip", tmp_path)


class MockArgs:
    def __init__(self):
        self.state = "all"
        self.plugin = "plugin1"
        self.force = False
        self.all = False


class Mockers:
    def __init__(self, mocker):
        self.mock_print = mocker.patch("kit.commands.plugin.print")
        self.mock_plugin_dict = mocker.patch("kit.commands.plugin.get_plugin_dict")
        self.mock_plugin_dict.return_value = geet_fake_dict()
        self.mock_dump_toml = mocker.patch("kit.commands.plugin.dump_toml")
