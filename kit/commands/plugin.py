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


PluginDict = Dict[str, str]


class InvalidPluingError(Exception):
    """InvalidPluingError exception raised for an invalid plugin"""


class PluingType(Enum):
    """Categories of files"""

    DIR = 1
    TARBALL = 2
    ZIP = 3


def get_plugin_type(plugin_path: Path) -> PluingType:
    """return plugin type"""
    if not plugin_path.exists():
        raise FileNotFoundError(f"File '{plugin_path}' not found")

    if plugin_path.is_dir():
        return PluingType.DIR

    if is_tarfile(plugin_path):
        return PluingType.TARBALL

    if is_zipfile(plugin_path):
        return PluingType.ZIP

    raise TypeError("This program only supports tarball or zip files")


def check_plugin_structure(plugin_path: Path, plugin_type: PluingType) -> str:
    """check the mínimum plugin structure (a directory with a plugin.py file)
    and return its name"""
    plugin_name = ""
    expected_file = "plugin.py"

    if PluingType.DIR == plugin_type:
        plugin_name = plugin_path.name
        if not (plugin_path / expected_file).exists():
            raise FileNotFoundError(
                f"File '{expected_file}' not found in '{plugin_name}'"
            )
        return plugin_name

    try:
        if PluingType.TARBALL == plugin_type:
            with tar_open(plugin_path) as f:
                plugin_name = f.getmembers()[0].name
                # getmember raises a KeyError if the file can not be found
                f.getmember(f"{plugin_name}/{expected_file}")
        elif PluingType.ZIP == plugin_type:
            with ZipFile(plugin_path) as f:
                plugin_name = f.infolist()[0].filename.replace("/", "")
                # getinfo raises a KeyError if the file can not be found
                f.getinfo(f"{plugin_name}/{expected_file}")
    except Exception as e:
        raise InvalidPluingError(
            f"File 'DIRECTORY/{expected_file}' not found in '{plugin_path.name}'"
        ) from e

    return plugin_name


def move_plugin_data(plugin_path: Path, plugin_type: PluingType) -> None:
    """Move the pluing data to ~/.hekit/plugins"""
    dst_path = PluginsConfig.ROOT_DIR
    if PluingType.DIR == plugin_type:
        copytree(plugin_path, dst_path / plugin_path.name)
    elif PluingType.TARBALL == plugin_type:
        with tar_open(plugin_path) as f:
            f.extractall(dst_path)
    elif PluingType.ZIP == plugin_type:
        with ZipFile(plugin_path) as f:
            f.extractall(dst_path)


def install_plugin(plugin_file: str, plugin_dict: PluginDict) -> None:
    """Install third party plugins"""
    plugin_path = Path(plugin_file).resolve()
    plugin_type = get_plugin_type(plugin_path)
    plugin_name = check_plugin_structure(plugin_path, plugin_type)

    # check if plugin is unique
    if plugin_name in plugin_dict.keys():
        print(f"Plugin {plugin_name} is already installed in the system")
        return

    move_plugin_data(plugin_path, plugin_type)

    # Update plugin dictionary
    plugin_dict[plugin_name] = PluginState.ENABLE
    print(f"Plugin {plugin_name} was installed successfully")


def remove_plugin_dir(plugin_name: str) -> None:
    """Delete the directory where the plugin is installed"""
    plugin_path = PluginsConfig.ROOT_DIR / plugin_name
    if file_exists(plugin_path):
        rmtree(plugin_path)


def remove_all_plugins(plugin_dict: PluginDict) -> None:
    """Remove all third party plugins"""
    user_answer = input("All plugins will be deleted. Do you want to continue? (y/n) ")
    if user_answer not in ("y", "Y"):
        return

    for plugin_name in plugin_dict.keys():
        remove_plugin_dir(plugin_name)

    plugin_dict.clear()
    print("All Plugins were uninstalled successfully")


def remove_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Remove a specific third party plugins"""
    if plugin_name not in plugin_dict.keys():
        print(f"Plugin {plugin_name} was not found in the system")
        return

    remove_plugin_dir(plugin_name)
    del plugin_dict[plugin_name]
    print(f"Plugin {plugin_name} was uninstalled successfully")


def enable_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Enable third party plugins"""
    if (
        plugin_name in plugin_dict.keys()
        and PluginState.ENABLE == plugin_dict[plugin_name]
    ):
        print(f"Plugin {plugin_name} is already enabled in the system")
        return

    plugin_dict[plugin_name] = PluginState.ENABLE
    print(f"Plugin {plugin_name} was enabled successfully")


def disable_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Disable third party plugins"""
    if plugin_name not in plugin_dict.keys():
        print(f"Plugin {plugin_name} was not found in the system")
        return
    if PluginState.DISABLE == plugin_dict[plugin_name]:
        print(f"Plugin {plugin_name} is already disabled in the system")
        return

    plugin_dict[plugin_name] = PluginState.DISABLE
    print(f"Plugin {plugin_name} was disabled successfully")


def list_plugins(plugin_dict: PluginDict, state: str) -> None:
    """Print the list of all plugins"""
    width_name = max(map(len, plugin_dict.keys()), default=0) + 3
    width_status = 10
    filtered_plugin_dict = (
        plugin_dict.items()
        if state == "all"
        else ((k, v) for k, v in plugin_dict.items() if state == v)
    )

    print(f"{'PLUGIN':{width_name}} {'STATE':{width_status}}")
    for k, v in filtered_plugin_dict:
        print(f"{k:{width_name}} {v:{width_status}}")


def handle_plugins(args) -> None:
    """Handle third party plugins"""
    if not file_exists(PluginsConfig.FILE):
        print("Please execute: hekit init --default-config")
        return

    # Get the plugins data
    plugin_dict = load_toml(PluginsConfig.FILE)[PluginsConfig.KEY]

    if hasattr(args, "state"):
        list_plugins(plugin_dict, args.state)
        return

    if hasattr(args, "plugin_to_install"):
        install_plugin(args.plugin_to_install, plugin_dict)
    elif hasattr(args, "plugin_to_remove"):
        if "ALL" == args.plugin_to_remove:
            remove_all_plugins(plugin_dict)
        else:
            remove_plugin(args.plugin_to_remove, plugin_dict)
    elif hasattr(args, "plugin_to_enable"):
        enable_plugin(args.plugin_to_enable, plugin_dict)
    elif hasattr(args, "plugin_to_disable"):
        disable_plugin(args.plugin_to_disable, plugin_dict)

    # Save changes in the plugins data
    sorted_plugin_dict = {PluginsConfig.KEY: dict(sorted(plugin_dict.items()))}
    dump_toml(PluginsConfig.FILE, sorted_plugin_dict)


def set_plugin_subparser(subparsers) -> None:
    """create the parser for the 'plugin' command"""
    parser_plugin = subparsers.add_parser(
        "plugins", description="handle third party plugins"
    )
    subparsers_plugin = parser_plugin.add_subparsers(help="sub-command help")

    # list options
    parser_install = subparsers_plugin.add_parser(
        "list", description="print the list of all plugins"
    )
    parser_install.add_argument(
        "--state",
        default="all",
        choices=["all", PluginState.ENABLE, PluginState.DISABLE],
        help="filter the plugins by their state",
    )

    # install options
    parser_install = subparsers_plugin.add_parser(
        "install", description="install a new plugin"
    )
    parser_install.add_argument(
        "plugin_to_install",
        type=validate_input,
        help="File with the plugin",
        metavar="PLUGIN",
    )
    parser_install.add_argument(
        "--force", action="store_true", help="forces the installation process"
    )

    # remove options
    parser_remove = subparsers_plugin.add_parser(
        "remove", description="remove a plugin"
    )
    parser_remove.add_argument(
        "plugin_to_remove",
        type=validate_input,
        help="plugin name. Use 'ALL' option to remove all plugins",
        metavar="PLUGIN",
    ).completer = plugins_enable_completer

    # enable options
    parser_enable = subparsers_plugin.add_parser(
        "enable", description="enable a plugin"
    )
    parser_enable.add_argument(
        "plugin_to_enable", type=validate_input, help="plugin name", metavar="PLUGIN"
    ).completer = plugins_disable_completer

    # disable options
    parser_disable = subparsers_plugin.add_parser(
        "disable", description="disable a plugin"
    )
    parser_disable.add_argument(
        "plugin_to_disable", type=validate_input, help="plugin name", metavar="PLUGIN"
    ).completer = plugins_enable_completer

    parser_plugin.set_defaults(fn=handle_plugins)
