# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from shutil import make_archive
from pathlib import Path
from kit.utils.constants import PluginsConfig, PluginState
from kit.commands.plugin import (
    InvalidPluginError,
    PluginType,
    load_plugins_config_file,
    update_plugins_config_file,
    get_plugin_type,
    check_plugin_structure,
    move_plugin_data,
    install_plugin,
    remove_plugin,
    update_plugin_state,
    list_plugins,
)


def test_load_plugins_config_file_file_not_found():
    """Verify that the SW raises an error
    when the toml file is not found"""
    plugin_name = "test.toml"
    with pytest.raises(FileNotFoundError) as exc_info:
        load_plugins_config_file(Path(plugin_name))
    assert (
        str(exc_info.value)
        == f"File '{plugin_name}' not found. Please execute: hekit init --default-config"
    )


def test_load_plugins_config_file_correct_file(tmp_path):
    """Verify that the SW returns a dict
    after reading a toml file"""
    plugin_name = tmp_path / "test.toml"
    create_config_file(plugin_name)

    act_dict = load_plugins_config_file(plugin_name)
    assert act_dict == get_fake_dict()


def test_update_plugins_config_file(tmp_path):
    """Verify that the SW saves an ordered
    dictionary in a toml file"""
    dict = {"w": "1", "t": "5", "a": "2", "j": "3"}
    order_dict = {"a": "2", "j": "3", "t": "5", "w": "1"}
    plugin_name = tmp_path / "test.toml"

    update_plugins_config_file(dict, plugin_name)
    assert order_dict == load_plugins_config_file(plugin_name)


def test_get_plugin_type_file_not_found():
    """Verify that the SW raises an error
    when the plugin file is not found"""
    plugin_name = "MyPlugin"
    with pytest.raises(FileNotFoundError) as exc_info:
        get_plugin_type(Path(plugin_name))
    assert str(exc_info.value) == f"File '{plugin_name}' not found"


def test_get_plugin_type_file_not_supported():
    """Verify that the SW raises an error
    when the plugin extension is wrong"""
    tests_path = Path(__file__).resolve().parent
    file = tests_path / "input_files/default.config"
    with pytest.raises(TypeError) as exc_info:
        get_plugin_type(file)
    assert str(exc_info.value) == "This program only supports tarball or zip files"


def test_get_plugin_type_dir(tmp_path):
    """Verify that the SW returns the correct plugin type (directory)"""
    plugin_path = create_plugins_files("test", tmp_path, PluginType.DIR)
    assert PluginType.DIR == get_plugin_type(plugin_path)


def test_get_plugin_type_tar(tmp_path):
    """Verify that the SW returns the correct plugin type (tarball)"""
    plugin_path = create_plugins_files("test", tmp_path, PluginType.TAR)
    assert PluginType.TAR == get_plugin_type(plugin_path)


def test_get_plugin_type_zip(tmp_path):
    """Verify that the SW returns the correct plugin type (zip)"""
    plugin_path = create_plugins_files("test", tmp_path, PluginType.ZIP)
    assert PluginType.ZIP == get_plugin_type(plugin_path)


def test_check_plugin_structure_dir_toml_not_found(tmp_path):
    """Verify that the SW raises an error when
    the plugin.py is not present in the directory"""
    plugin_name = "test"
    plugin_type = PluginType.DIR
    plugin_path = create_plugins_files(plugin_name, tmp_path, plugin_type)

    with pytest.raises(InvalidPluginError) as exc_info:
        check_plugin_structure(plugin_path, plugin_type)
    assert str(exc_info.value) == f"File 'plugin.toml' not found in '{plugin_name}'"


def test_check_plugin_structure_dir_correct_plugin(tmp_path):
    """Verify that the SW returns the plugin name
    after checking a directory with plugin.py"""
    plugin_name = "test"
    plugin_type = PluginType.DIR
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, plugin_type, with_file=True
    )
    act_name = check_plugin_structure(plugin_path, plugin_type)[0]
    assert act_name["name"] == plugin_name
    assert act_name["version"] == "1.0.0"
    assert act_name["start"] == "plugin.py"


def test_check_plugin_structure_zip_plugin_not_found(tmp_path):
    """Verify that the SW raises an error when
    the plugin.py is not present in the zip file"""
    plugin_type = PluginType.ZIP
    plugin_path = create_plugins_files("test", tmp_path, plugin_type)

    with pytest.raises(InvalidPluginError) as exc_info:
        check_plugin_structure(plugin_path, plugin_type)
    assert (
        str(exc_info.value) == f"File 'plugin.toml' not found in '{plugin_path.name}'"
    )


def test_check_plugin_structure_zip_correct_plugin(tmp_path):
    """Verify that the SW returns the plugin name
    after checking a zip file with plugin.py"""
    plugin_name = "test"
    plugin_type = PluginType.ZIP
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, plugin_type, with_file=True
    )

    act_name = check_plugin_structure(plugin_path, plugin_type)[0]
    assert act_name["name"] == plugin_name
    assert act_name["version"] == "1.0.0"
    assert act_name["start"] == "plugin.py"


def test_check_plugin_structure_tar_plugin_not_found(tmp_path):
    """Verify that the SW raises an error when
    the plugin.py is not present in the tarball file"""
    plugin_type = PluginType.TAR
    plugin_path = create_plugins_files("test", tmp_path, plugin_type)

    with pytest.raises(InvalidPluginError) as exc_info:
        check_plugin_structure(plugin_path, plugin_type)
    assert (
        str(exc_info.value) == f"File 'plugin.toml' not found in '{plugin_path.name}'"
    )


def test_check_plugin_structure_tar_correct_plugin(tmp_path):
    """Verify that the SW returns the plugin name
    after checking a tarball file with plugin.py"""
    plugin_name = "test"
    plugin_type = PluginType.TAR
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, plugin_type, with_file=True
    )

    act_name = check_plugin_structure(plugin_path, plugin_type)[0]
    assert act_name["name"] == plugin_name
    assert act_name["version"] == "1.0.0"
    assert act_name["start"] == "plugin.py"


def test_move_plugin_data_dir(tmp_path):
    """Verify that the SW copies correctly the plugin in a directory"""
    plugin_name = "test"
    plugin_type = PluginType.DIR
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, plugin_type, with_file=True
    )
    dest_path = create_tmp_directory(tmp_path)

    move_plugin_data(plugin_name, plugin_path, plugin_type, dest_path)
    assert (dest_path / plugin_name).exists()


def test_move_plugin_data_tar(tmp_path):
    """Verify that the SW extracts correctly the plugin in a tarball file"""
    plugin_name = "test"
    plugin_type = PluginType.TAR
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, plugin_type, with_file=True
    )
    dest_path = create_tmp_directory(tmp_path)

    move_plugin_data(plugin_name, plugin_path, plugin_type, dest_path)
    assert (dest_path / plugin_name).exists()


def test_move_plugin_data_zip(tmp_path):
    """Verify that the SW extracts correctly the plugin in a zip file"""
    plugin_name = "test"
    plugin_type = PluginType.ZIP
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, plugin_type, with_file=True
    )
    dest_path = create_tmp_directory(tmp_path)

    move_plugin_data(plugin_name, plugin_path, plugin_type, dest_path)
    assert (dest_path / plugin_name).exists()


def test_install_plugin_present_file(mocker, tmp_path):
    """Verify that the SW prints a message when
    trying to install a plugin already installed"""
    plugin_name = "plugin1"
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, PluginType.DIR, with_file=True
    )

    args = MockArgs()
    args.plugin = plugin_path
    mockers = Mockers(mocker)

    install_plugin(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with(
        f"{plugin_name} version 1.0.0 is already installed on the system"
    )


def test_install_plugin_present_file_force_flag(mocker, tmp_path):
    """Verify that the SW forces the installation process
    when using --force flag"""
    plugin_name = "plugin1"
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, PluginType.DIR, with_file=True
    )

    args = MockArgs()
    args.plugin = plugin_path
    args.force = True
    mockers = Mockers(mocker)

    install_plugin(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with(
        f"Plugin {plugin_name} was installed successfully"
    )


def test_install_plugin_dir(mocker, tmp_path):
    """Verify that the SW installs a plugin in a directory"""
    plugin_name = "test1"
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, PluginType.DIR, with_file=True
    )

    args = MockArgs()
    args.plugin = plugin_path
    mockers = Mockers(mocker)

    install_plugin(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with(
        f"Plugin {plugin_name} was installed successfully"
    )


def test_install_plugin_tar(mocker, tmp_path):
    """Verify that the SW installs a plugin in a tarball file"""
    plugin_name = "test2"
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, PluginType.TAR, with_file=True
    )

    args = MockArgs()
    args.plugin = plugin_path
    mockers = Mockers(mocker)

    install_plugin(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with(
        f"Plugin {plugin_name} was installed successfully"
    )


def test_install_plugin_zip(mocker, tmp_path):
    """Verify that the SW installs a plugin in a zip file"""
    plugin_name = "test3"
    plugin_path = create_plugins_files(
        plugin_name, tmp_path, PluginType.ZIP, with_file=True
    )

    args = MockArgs()
    args.plugin = plugin_path
    mockers = Mockers(mocker)

    install_plugin(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with(
        f"Plugin {plugin_name} was installed successfully"
    )


def test_remove_plugin_name_not_found(mocker):
    """Verify that the SW prints a message when
    trying to remove a plugin that is not on the system"""
    args = MockArgs()
    args.plugin = "test"
    mockers = Mockers(mocker)

    remove_plugin(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_remove_dir.assert_not_called()
    mockers.mock_print.assert_called_with(
        f"Plugin {args.plugin} was not found on the system"
    )


def test_remove_plugin_name_correct(mocker):
    """Verify that the SW removes a specific plugin"""
    args = MockArgs()
    args.plugin = "plugin1"
    mockers = Mockers(mocker)

    remove_plugin(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_remove_dir.assert_called_once()
    mockers.mock_print.assert_called_with(
        f"Plugin {args.plugin} was uninstalled successfully"
    )


def test_remove_plugin_all(mocker):
    """Verify that the SW removes all plugins on the system"""
    args = MockArgs()
    args.all = True
    mockers = Mockers(mocker)
    mock_input = mocker.patch("kit.commands.plugin.input", return_value="y")

    remove_plugin(args)
    mock_input.assert_called_once()
    assert 2 == mockers.mock_remove_dir.call_count
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with("All plugins were uninstalled successfully")


def test_update_plugin_state_unknown_plugin(mocker):
    """Verify that the SW reports a message
    when the plugin is not on the system"""
    args = MockArgs()
    args.plugin = "test"
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with(
        f"Plugin {args.plugin} was not found on the system"
    )


def test_update_plugin_state_already_enabled(mocker):
    """Verify that the SW reports a message
    when the plugin is already enabled"""
    args = MockArgs()
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with(
        f"Plugin {args.plugin} is already enabled on the system"
    )


def test_update_plugin_state_already_disabled(mocker):
    """Verify that the SW reports a message
    when the plugin is already disabled"""
    args = MockArgs()
    args.plugin = "plugin2"
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_not_called()
    mockers.mock_print.assert_called_with(
        f"Plugin {args.plugin} is already disabled on the system"
    )


def test_update_plugin_state_enable(mocker):
    """Verify that the SW enables a plugin"""
    args = MockArgs()
    args.plugin = "plugin2"
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with(
        f"Plugin {args.plugin} was enabled successfully"
    )


def test_update_plugin_state_disable(mocker):
    """Verify that the SW disables a plugin"""
    args = MockArgs()
    args.plugin = "plugin1"
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    update_plugin_state(args)
    mockers.mock_dump_toml.assert_called_once()
    mockers.mock_print.assert_called_with(
        f"Plugin {args.plugin} was disabled successfully"
    )


def test_list_plugins_all(mocker):
    """Verify that the SW prints all plugins"""
    args = MockArgs()
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 3 == mockers.mock_print.call_count
    mockers.mock_print.assert_any_call("plugin2    1.0.0      disabled  ")
    mockers.mock_print.assert_any_call("plugin1    1.0.0      enabled   ")


def test_list_plugins_enable(mocker):
    """Verify that the SW prints only enabled plugins"""
    args = MockArgs()
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with(f"plugin1    1.0.0      enabled   ")


def test_list_plugins_disable(mocker):
    """Verify that the SW prints only disabled plugins"""
    args = MockArgs()
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with("plugin2    1.0.0      disabled  ")


"""Utilities used by the tests"""


def get_fake_dict():
    return {
        "plugin1": {"version": "1.0.0", "state": PluginState.ENABLE},
        "plugin2": {"version": "1.0.0", "state": PluginState.DISABLE},
    }


def create_tmp_directory(tmp_path):
    dest_path = tmp_path / "tmp"
    dest_path.mkdir(exist_ok=True)
    return dest_path


def create_plugins_files(plugin_name, tmp_path, plugin_type, with_file=False):
    plugin_path = tmp_path / plugin_name
    plugin_path.mkdir(exist_ok=True)

    if with_file:
        plugin_file = plugin_path / "plugin.py"
        with plugin_file.open("w") as f:
            f.write("test")

        toml_file = plugin_path / "plugin.toml"
        with toml_file.open("w") as f:
            f.write(
                "[plugin]\n"
                f'name = "{plugin_name}"\n'
                'version = "1.0.0"\n'
                'start = "plugin.py"\n'
            )

    if plugin_type == PluginType.DIR:
        return tmp_path / plugin_name

    if plugin_type == PluginType.TAR:
        make_archive(plugin_path, "gztar", root_dir=tmp_path, base_dir=plugin_name)
        return tmp_path / f"{plugin_name}.tar.gz"

    if plugin_type == PluginType.ZIP:
        make_archive(plugin_path, "zip", root_dir=tmp_path)
        return tmp_path / f"{plugin_name}.zip"


def create_config_file(filepath):
    with filepath.open("w") as f:
        for k, v in get_fake_dict().items():
            version, state = v["version"], v["state"]
            f.write(
                f"[{PluginsConfig.KEY}.{k}]\n"
                f'version = "{version}"\n'
                f'state = "{state}"\n'
            )


class MockArgs:
    def __init__(self):
        self.state = "all"
        self.plugin = "plugin1"
        self.force = False
        self.all = False
        self.hekit_parsers_list = {}


class Mockers:
    def __init__(self, mocker):
        self.mock_print = mocker.patch("kit.commands.plugin.print")
        self.mock_get_dict = mocker.patch(
            "kit.commands.plugin.load_plugins_config_file"
        )
        self.mock_get_dict.return_value = get_fake_dict()
        self.mock_dump_toml = mocker.patch("kit.commands.plugin.dump_toml")
        self.mock_move_data = mocker.patch("kit.commands.plugin.move_plugin_data")
        self.mock_remove_dir = mocker.patch("kit.commands.plugin.remove_plugin_data")
