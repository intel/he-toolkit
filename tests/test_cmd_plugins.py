# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from shutil import make_archive
from pathlib import Path
from kit.utils.constants import PluginsConfig, PluginState
from kit.commands.plugin import (
    InvalidPluginError,
    PluginType,
    get_plugin_dict,
    update_plugin_file,
    get_plugin_type,
    check_plugin_structure,
    move_plugin_data,
    install_plugin,
    remove_plugin,
    update_plugin_state,
    list_plugins,
)


def test_get_plugin_dict_not_found():
    """Verify that the SW raises an error
    when the toml file is not found"""
    plugin_name = "test.toml"
    with pytest.raises(FileNotFoundError) as exc_info:
        get_plugin_dict(Path(plugin_name))
    assert (
        str(exc_info.value)
        == f"File '{plugin_name}' not found. Please execute: hekit init --default-config"
    )


def test_get_plugin_dict_correct_file(tmp_path):
    """Verify that the SW returns a dict
    after reading a toml file"""
    plugin_name = tmp_path / "test.toml"
    create_config_file(plugin_name)

    act_dict = get_plugin_dict(plugin_name)
    assert act_dict == geet_fake_dict()


def test_update_plugin_file(tmp_path):
    """Verify that the SW saves an ordered
    dictionary in a toml file"""
    dict = {"w": "1", "t": "5", "a": "2", "j": "3"}
    order_dict = {"a": "2", "j": "3", "t": "5", "w": "1"}
    plugin_name = tmp_path / "test.toml"

    update_plugin_file(dict, plugin_name)
    assert order_dict == get_plugin_dict(plugin_name)


def test_get_plugin_type_all_valid(tmp_path):
    """Verify that the SW returns the correct plugin type"""
    plugin_name = "MyPlugin"
    create_plugins_files(plugin_name, tmp_path)
    assert PluginType.DIR == get_plugin_type(tmp_path / plugin_name)
    assert PluginType.TAR == get_plugin_type(tmp_path / f"{plugin_name}.tar.gz")
    assert PluginType.ZIP == get_plugin_type(tmp_path / f"{plugin_name}.zip")


def test_get_plugin_type_not_found():
    """Verify that the SW raises an error
    when the plugin file is not found"""
    plugin_name = "MyPlugin"
    with pytest.raises(FileNotFoundError) as exc_info:
        get_plugin_type(Path(plugin_name))
    assert str(exc_info.value) == f"File '{plugin_name}' not found"


def test_get_plugin_type_not_supported():
    """Verify that the SW return a dict
    that was read from a toml file"""
    tests_path = Path(__file__).resolve().parent
    file = tests_path / "input_files/default.config"
    with pytest.raises(TypeError) as exc_info:
        get_plugin_type(file)
    assert str(exc_info.value) == "This program only supports tarball or zip files"


def test_check_plugin_structure_dir_plugin_not_found(tmp_path):
    """Verify that the SW raises an error when
    the plugin.py is not present in the directory"""
    plugin_name = "test"
    create_plugins_files(plugin_name, tmp_path, type="dir")
    plugin_path = tmp_path / plugin_name

    plugin_type = get_plugin_type(plugin_path)
    with pytest.raises(FileNotFoundError) as exc_info:
        check_plugin_structure(plugin_path, plugin_type)
    assert PluginType.DIR == plugin_type
    assert str(exc_info.value) == f"File 'plugin.py' not found in '{plugin_name}'"


def test_check_plugin_structure_dir_correct_plugin(tmp_path):
    """Verify that the SW returns the plugin name
    after checking a directory with plugin.py"""
    plugin_name = "test"
    create_plugins_files(plugin_name, tmp_path, type="dir", with_file=True)
    plugin_path = tmp_path / plugin_name

    plugin_type = get_plugin_type(plugin_path)
    act_name = check_plugin_structure(plugin_path, plugin_type)
    assert PluginType.DIR == plugin_type
    assert act_name == plugin_name


def test_check_plugin_structure_zip_plugin_not_found(tmp_path):
    """Verify that the SW raises an error when
    the plugin.py is not present in the zip file"""
    plugin_name = "test"
    create_plugins_files(plugin_name, tmp_path, type="zip")
    plugin_path = tmp_path / f"{plugin_name}.zip"

    plugin_type = get_plugin_type(plugin_path)
    with pytest.raises(InvalidPluginError) as exc_info:
        check_plugin_structure(plugin_path, plugin_type)
    assert PluginType.ZIP == plugin_type
    assert (
        str(exc_info.value)
        == f"File 'DIRECTORY/plugin.py' not found in '{plugin_name}.zip'"
    )


def test_check_plugin_structure_zip_correct_plugin(tmp_path):
    """Verify that the SW returns the plugin name
    after checking a zip file with plugin.py"""
    plugin_name = "test"
    create_plugins_files(plugin_name, tmp_path, type="zip", with_file=True)
    plugin_path = tmp_path / f"{plugin_name}.zip"

    plugin_type = get_plugin_type(plugin_path)
    act_name = check_plugin_structure(plugin_path, plugin_type)
    assert PluginType.ZIP == plugin_type
    assert act_name == plugin_name


def test_check_plugin_structure_tar_plugin_not_found(tmp_path):
    """Verify that the SW raises an error when
    the plugin.py is not present in the tarball file"""
    plugin_name = "test"
    create_plugins_files(plugin_name, tmp_path, type="tar")
    plugin_path = tmp_path / f"{plugin_name}.tar.gz"

    plugin_type = get_plugin_type(plugin_path)
    with pytest.raises(InvalidPluginError) as exc_info:
        check_plugin_structure(plugin_path, plugin_type)
    assert PluginType.TAR == plugin_type
    assert (
        str(exc_info.value)
        == f"File 'DIRECTORY/plugin.py' not found in '{plugin_name}.tar.gz'"
    )


def test_check_plugin_structure_tar_correct_plugin(tmp_path):
    """Verify that the SW returns the plugin name
    after checking a tarball file with plugin.py"""
    plugin_name = "test"
    create_plugins_files(plugin_name, tmp_path, type="tar", with_file=True)
    plugin_path = tmp_path / f"{plugin_name}.tar.gz"

    plugin_type = get_plugin_type(plugin_path)
    act_name = check_plugin_structure(plugin_path, plugin_type)
    assert PluginType.TAR == plugin_type
    assert act_name == plugin_name


def test_update_plugin_state_unknown_plugin(mocker):
    """Verify that the SW reports a message
    when the plugin is not in the system"""
    args = MockArgs()
    args.plugin = "test"
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with("Plugin test was not found in the system")


def test_update_plugin_state_already_enabled(mocker):
    """Verify that the SW reports a message
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
    """Verify that the SW reports a message
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
    """Verify that the SW enables a plugin"""
    args = MockArgs()
    args.plugin = "plugin2"
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with("Plugin plugin2 was enabled successfully")


def test_update_plugin_state_disable(mocker):
    """Verify that the SW disables a plugin"""
    args = MockArgs()
    args.plugin = "plugin1"
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with("Plugin plugin1 was disabled successfully")


def test_list_plugins_all(mocker):
    """Verify that the SW prints all plugins"""
    args = MockArgs()
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 3 == mockers.mock_print.call_count
    mockers.mock_print.assert_any_call("plugin2    disabled  ")
    mockers.mock_print.assert_any_call("plugin1    enabled   ")


def test_list_plugins_enable(mocker):
    """Verify that the SW prints only enabled plugins"""
    args = MockArgs()
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with("plugin1    enabled   ")


def test_list_plugins_disable(mocker):
    """Verify that the SW prints only disabled plugins"""
    args = MockArgs()
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with("plugin2    disabled  ")


"""Utilities used by the tests"""


def geet_fake_dict():
    return {"plugin1": PluginState.ENABLE, "plugin2": PluginState.DISABLE}


def create_plugins_files(plugin_name, tmp_path, type="all", with_file=False):
    plugin_path = tmp_path / plugin_name
    plugin_path.mkdir(exist_ok=True)

    if with_file:
        plugin_file = plugin_path / "plugin.py"
        with plugin_file.open("w") as f:
            f.write("test")

    if type in ["all", "tar"]:
        make_archive(plugin_path, "gztar", root_dir=tmp_path, base_dir=plugin_name)

    if type in ["all", "zip"]:
        make_archive(plugin_path, "zip", root_dir=tmp_path)


def create_config_file(filepath):
    with filepath.open("w") as f:
        f.write(f"[{PluginsConfig.KEY}]\n")
        for k, v in geet_fake_dict().items():
            f.write(f'{k} = "{v}"\n')


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
