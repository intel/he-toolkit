# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the usage of third party plugins"""

from enum import Enum
from pathlib import Path
from shutil import rmtree, copytree
from tarfile import is_tarfile, open as tar_open
from typing import Dict
from zipfile import is_zipfile, ZipFile
from kit.utils.constants import PluginsConfig, PluginState
from kit.utils.files import load_toml, dump_toml, file_exists
from kit.utils.subparsers import validate_input
from kit.utils.tab_completion import plugins_enable_completer, plugins_disable_completer


ConfigDict = Dict[str, str]
PluginDict = Dict[str, str]


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
        return load_toml(source_file)[PluginsConfig.KEY]
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"{str(e)}. Please execute: hekit init --default-config"
        ) from e


def update_plugins_config_file(
    config_dict: ConfigDict, dest_file: Path = PluginsConfig.FILE
) -> None:
    """Save changes in the plugins data"""
    sorted_dict = {PluginsConfig.KEY: dict(sorted(config_dict.items()))}
    dump_toml(dest_file, sorted_dict)


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


def check_plugin_structure(plugin_path: Path, plugin_type: PluginType) -> str:
    """Check the minimum plugin structure (a directory with a plugin.py file)
    and return its name"""
    plugin_name = ""
    expected_file = "plugin.py"

    if PluginType.DIR == plugin_type:
        plugin_name = plugin_path.name
        if not (plugin_path / expected_file).exists():
            raise FileNotFoundError(
                f"File '{expected_file}' not found in '{plugin_name}'"
            )
        return plugin_name

    try:
        if PluginType.TAR == plugin_type:
            with tar_open(plugin_path) as f:
                plugin_name = f.getmembers()[0].name
                # getmember raises a KeyError if the file cannot be found
                f.getmember(f"{plugin_name}/{expected_file}")
        elif PluginType.ZIP == plugin_type:
            with ZipFile(plugin_path) as f:
                plugin_name = f.infolist()[0].filename.replace("/", "")
                # getinfo raises a KeyError if the file cannot be found
                f.getinfo(f"{plugin_name}/{expected_file}")
    except Exception as e:
        raise InvalidPluginError(
            f"File 'DIRECTORY/{expected_file}' not found in '{plugin_path.name}'"
        ) from e

    return plugin_name


def move_plugin_data(
    plugin_path: Path, plugin_type: PluginType, dest_path: Path = PluginsConfig.ROOT_DIR
) -> None:
    """Move the plugin data to ~/.hekit/plugins"""
    if PluginType.DIR == plugin_type:
        copytree(plugin_path, dest_path / plugin_path.name)
    elif PluginType.TAR == plugin_type:
        with tar_open(plugin_path) as f:
            f.extractall(dest_path)
    elif PluginType.ZIP == plugin_type:
        with ZipFile(plugin_path) as f:
            f.extractall(dest_path)


def install_plugin(args) -> None:
    """Install third party plugins"""
    config_dict = load_plugins_config_file()
    plugin_path = Path(args.plugin).resolve()
    plugin_type = get_plugin_type(plugin_path)
    plugin_name = check_plugin_structure(plugin_path, plugin_type)
    if args.force:
        remove_plugin_dir(plugin_name)
    elif plugin_name in config_dict.keys():
        print(f"Plugin {plugin_name} is already installed in the system")
        return

    move_plugin_data(plugin_path, plugin_type)

    # Update plugin dictionary
    config_dict[plugin_name] = PluginState.ENABLE
    update_plugins_config_file(config_dict)
    print(f"Plugin {plugin_name} was installed successfully")


def remove_plugin_dir(
    plugin_name: str, root_dir: Path = PluginsConfig.ROOT_DIR
) -> None:
    """Delete the directory where the plugin is installed"""
    plugin_path = root_dir / plugin_name
    if file_exists(plugin_path):
        rmtree(plugin_path)


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
            remove_plugin_dir(plugin_name)

        config_dict.clear()
        print("All plugins were uninstalled successfully")
    else:
        plugin_name = args.plugin
        if not plugin_name:
            raise ValueError("A plugin name should be specified as argument")

        # Remove a specific third party plugins
        if plugin_name not in config_dict.keys():
            print(f"Plugin {plugin_name} was not found in the system")
            return

        remove_plugin_dir(plugin_name)
        del config_dict[plugin_name]
        print(f"Plugin {plugin_name} was uninstalled successfully")

    update_plugins_config_file(config_dict)


def update_plugin_state(args) -> None:
    """Enable third party plugins"""
    config_dict = load_plugins_config_file()
    plugin_name = args.plugin
    plugin_state = args.state

    if plugin_name not in config_dict.keys():
        print(f"Plugin {plugin_name} was not found in the system")
        return
    if plugin_state == config_dict[plugin_name]:
        print(f"Plugin {plugin_name} is already {plugin_state} in the system")
        return

    config_dict[plugin_name] = plugin_state
    update_plugins_config_file(config_dict)
    print(f"Plugin {plugin_name} was {plugin_state} successfully")


def list_plugins(args) -> None:
    """Print the list of all plugins"""
    config_dict = load_plugins_config_file()
    state = args.state

    width_name = max(map(len, config_dict.keys()), default=0) + 3
    width_status = 10
    filtered_dict = (
        config_dict.items()
        if state == "all"
        else ((k, v) for k, v in config_dict.items() if state == v)
    )

    print(f"{'PLUGIN':{width_name}} {'STATE':{width_status}}")
    for k, v in filtered_dict:
        print(f"{k:{width_name}} {v:{width_status}}")


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
