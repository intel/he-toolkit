# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the usage of third party plugins"""

from enum import Enum
from pathlib import Path
from shutil import rmtree, copytree
from tarfile import is_tarfile, open as tar_open
from typing import Dict, List
from zipfile import is_zipfile, ZipFile
from toml import loads as toml_loads
from kit.utils.constants import PluginsConfig, PluginState
from kit.utils.files import load_toml, dump_toml
from kit.utils.subparsers import validate_input
from kit.utils.tab_completion import plugins_enable_completer, plugins_disable_completer


ConfigDict = Dict[str, List[Dict[str, str]]]
PluginsList = List[Dict[str, str]]


class InvalidPluginError(Exception):
    """InvalidPluginError exception raised for an invalid plugin"""


class PluginType(Enum):
    """Categories of files"""

    DIR = 1
    TAR = 2
    ZIP = 3


def load_plugins_config_file(source_file: Path = PluginsConfig.FILE) -> ConfigDict:
    """Return plugins dictionary"""
    try:
        # Get the plugins data
        return load_toml(source_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"{str(e)}. Please execute: hekit init --default-config"
        ) from e


def update_plugins_config_file(
    config_dict: ConfigDict, dest_file: Path = PluginsConfig.FILE
) -> None:
    """Save changes in the plugins data"""
    # sorted_dict = {PluginsConfig.KEY: dict(sorted(config_dict.items()))}
    dump_toml(dest_file, config_dict)


def get_plugin_type(plugin_path: Path) -> PluginType:
    """Return plugin type"""
    if not plugin_path.exists():
        raise FileNotFoundError(f"File '{plugin_path}' not found")

    if plugin_path.is_dir():
        return PluginType.DIR

    if is_tarfile(plugin_path):
        return PluginType.TAR

    if is_zipfile(plugin_path):
        return PluginType.ZIP

    raise TypeError("This program only supports tarball or zip files")


def check_plugin_structure(plugin_path: Path, plugin_type: PluginType) -> PluginsList:
    """Check the minimum plugin structure (a directory with a plugin.py file)
    and return its name"""
    plugins_data_list = []
    exp_toml = "plugin.toml"
    exp_file = ""

    try:
        if PluginType.DIR == plugin_type:
            plugin_dict = load_toml(plugin_path / exp_toml)
            exp_file = plugin_path / plugin_dict["plugin"]["start"]
            if not Path(exp_file).exists():
                raise FileNotFoundError()
            plugins_data_list.append(plugin_dict["plugin"])

        elif PluginType.TAR == plugin_type:
            with tar_open(plugin_path) as f:
                # get the list of plugin.toml files
                tar_toml_list = [
                    item.name for item in f.getmembers() if exp_toml in item.name
                ]

                # getmember and extractfile raise a KeyError if the file cannot be found
                for toml_file in tar_toml_list:
                    # Verify the toml file is in a directory
                    dir_name = toml_file.split("/")[0]
                    f.getmember(dir_name)

                    # Read the toml file and check that the file
                    # defined in "start" is present
                    with f.extractfile(toml_file) as file:  # type: ignore[union-attr]
                        plugin_dict = toml_loads(file.read().decode("utf-8"))
                        exp_file = f'{dir_name}/{plugin_dict["plugin"]["start"]}'
                        f.getmember(exp_file)
                        plugins_data_list.append(plugin_dict["plugin"])

        elif PluginType.ZIP == plugin_type:
            with ZipFile(plugin_path) as f:
                # get the list of plugin.toml files
                zip_toml_list = [
                    item.filename for item in f.infolist() if exp_toml in item.filename
                ]

                # getinfo and open raise a KeyError if the file cannot be found
                for toml_file in zip_toml_list:
                    # Verify the toml file is in a directory
                    dir_name = toml_file.split("/")[0]
                    f.getinfo(f"{dir_name}/")

                    # Read the toml file and check that the file
                    # defined in "start" is present
                    with f.open(toml_file) as file:
                        plugin_dict = toml_loads(file.read().decode("utf-8"))
                        exp_file = f'{dir_name}/{plugin_dict["plugin"]["start"]}'
                        f.getinfo(exp_file)
                        plugins_data_list.append(plugin_dict["plugin"])

    except (FileNotFoundError, KeyError) as e:
        raise InvalidPluginError(
            f"File '{exp_file}' not found in '{plugin_path.name}'"
        ) from e

    return plugins_data_list


def move_plugin_data(
    plugin_name: str, plugin_path: Path, plugin_type: PluginType
) -> None:
    """Move the plugin data to ~/.hekit/plugins"""
    dest_path = PluginsConfig.ROOT_DIR

    if PluginType.DIR == plugin_type:
        copytree(plugin_path, dest_path / plugin_name)
    elif PluginType.TAR == plugin_type:
        with tar_open(plugin_path) as f:
            tar_items = [item for item in f.getmembers() if plugin_name in item.name]
            f.extractall(dest_path, tar_items)
    elif PluginType.ZIP == plugin_type:
        with ZipFile(plugin_path) as f:
            zip_items = [item for item in f.infolist() if plugin_name in item.filename]
            f.extractall(dest_path, zip_items)


def is_version_present(plugins_list, version):
    """Verify if the version is already installed"""
    for plugin_config in plugins_list:
        if plugin_config["version"] == version:
            return True

    return False


def install_plugin(args) -> None:
    """Install third party plugins"""
    config_dict = load_plugins_config_file()
    plugin_path = Path(args.plugin).resolve()
    plugin_type = get_plugin_type(plugin_path)
    plugins_list = check_plugin_structure(plugin_path, plugin_type)

    for plugin_dict in plugins_list:
        plugin_name = plugin_dict["name"]
        if args.force:
            rmtree(PluginsConfig.ROOT_DIR / plugin_name)
        elif plugin_name in config_dict.keys():
            if is_version_present(config_dict[plugin_name], plugin_dict["version"]):
                print(
                    f"Plugin {plugin_name} {plugin_dict['version']} is already installed in the system"
                )
                continue

            config_dict[plugin_name].append(
                {"version": plugin_dict["version"], "status": PluginState.ENABLE}
            )
        else:
            config_dict[plugin_name] = [
                {"version": plugin_dict["version"], "status": PluginState.ENABLE}
            ]

        move_plugin_data(plugin_name, plugin_path, plugin_type)

        # Update plugin dictionary
        update_plugins_config_file(config_dict)
        print(f"Plugin {plugin_name} was installed successfully")


def remove_plugin(args) -> None:
    """Remove third party plugins"""
    config_dict = load_plugins_config_file()

    if args.all:
        # Remove all third party plugins
        user_answer = input(
            "All plugins will be deleted. Do you want to continue? (y/n) "
        )
        if user_answer not in ("y", "Y"):
            return

        for plugin_name in config_dict.keys():
            rmtree(PluginsConfig.ROOT_DIR / plugin_name)

        config_dict.clear()
        print("All plugins were uninstalled successfully")
    else:
        plugin_name = args.plugin
        if not plugin_name:
            raise ValueError("A plugin name should be specified as argument")

        # Remove a specific third party plugins
        if plugin_name not in config_dict.keys():
            # TODO check version
            print(f"Plugin {plugin_name} was not found in the system")
            return

        rmtree(PluginsConfig.ROOT_DIR / plugin_name)
        del config_dict[plugin_name]
        print(f"Plugin {plugin_name} was uninstalled successfully")

    update_plugins_config_file(config_dict)


def update_plugin_state(args) -> None:
    """Enable third party plugins"""
    config_dict = load_plugins_config_file()
    plugin_name = args.plugin
    plugin_state = args.state

    if plugin_name not in config_dict.keys():
        # TODO check version
        print(f"Plugin {plugin_name} was not found in the system")
        return

    for plugin_config in config_dict[plugin_name]:
        if plugin_config["state"] == plugin_state:
            print(f"Plugin {plugin_name} is already {plugin_state} in the system")
            return

    # config_dict[plugin_name] = (config_dict[plugin_name][0], plugin_state)
    update_plugins_config_file(config_dict)
    print(f"Plugin {plugin_name} was {plugin_state} successfully")


def list_plugins(args) -> None:
    """Print the list of all plugins"""
    config_dict = load_plugins_config_file()
    state = args.state

    width_name = max(map(len, config_dict.keys()), default=0) + 3
    width_status = 10

    print(
        f"{'PLUGIN':{width_name}} {'Version':{width_status}} {'STATE':{width_status}}"
    )
    for plugin_name, plugin_list in config_dict.items():
        for plugin_dict in plugin_list:
            if state in (plugin_dict["status"], "all"):
                print(
                    f"{plugin_name:{width_name}} {plugin_dict['version']:{width_status}} {plugin_dict['status']:{width_status}}"
                )


def set_plugin_subparser(subparsers) -> None:
    """Create the parser for the 'plugin' command"""
    parser_plugin = subparsers.add_parser(
        "plugins", description="handle third party plugins"
    )
    subparsers_plugin = parser_plugin.add_subparsers(help="sub-command help")

    # list options
    parser_list = subparsers_plugin.add_parser(
        "list", description="print the list of all plugins"
    )
    parser_list.add_argument(
        "--state",
        default="all",
        choices=["all", PluginState.ENABLE, PluginState.DISABLE],
        help="filter the plugins by their state",
    )
    parser_list.set_defaults(fn=list_plugins)

    # install options
    parser_install = subparsers_plugin.add_parser(
        "install", description="install a new plugin"
    )
    parser_install.add_argument(
        "plugin",
        type=validate_input,
        help="File with the plugin",
    )
    parser_install.add_argument(
        "--force", action="store_true", help="forces the installation process"
    )
    parser_install.set_defaults(fn=install_plugin)

    # remove options
    parser_remove = subparsers_plugin.add_parser(
        "remove", description="remove a plugin"
    )
    parser_remove.add_argument(
        "plugin",
        type=validate_input,
        help="plugin name",
        nargs="?",
        default="",
    ).completer = plugins_enable_completer
    parser_remove.add_argument(
        "--all",
        action="store_true",
        help="Remove all plugins in the system",
    )
    parser_remove.set_defaults(fn=remove_plugin)

    # enable options
    parser_enable = subparsers_plugin.add_parser(
        "enable", description="enable a plugin"
    )
    parser_enable.add_argument(
        "plugin", type=validate_input, help="plugin name"
    ).completer = plugins_disable_completer
    parser_enable.set_defaults(fn=update_plugin_state, state=PluginState.ENABLE)

    # disable options
    parser_disable = subparsers_plugin.add_parser(
        "disable", description="disable a plugin"
    )
    parser_disable.add_argument(
        "plugin", type=validate_input, help="plugin name"
    ).completer = plugins_enable_completer
    parser_disable.set_defaults(fn=update_plugin_state, state=PluginState.DISABLE)
