# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the usage of third party plugins"""

from tarfile import open as open_tar
from pathlib import Path
from shutil import rmtree
from typing import Dict, List, Tuple
from kit.utils.subparsers import validate_input
from kit.utils.files import load_toml, dump_toml
from kit.utils.constants import Constants


PluginDict = Dict[str, str]


def get_enabled_plugins():
    """Return a list of plugins that are enabled"""
    plugin_toml_file = Constants.plugins_work_area / "plugins.toml"
    plugin_data = load_toml(plugin_toml_file)
    plugin_dict = plugin_data["plugins"]

    enabled_plugins = [k for k, v in plugin_dict.items() if v == "enabled"]
    return enabled_plugins


def list_plugins(plugin_dict: PluginDict) -> None:
    """Print the list of all plugins"""
    width_name = max(map(len, plugin_dict.keys()), default=0) + 3
    width_status = 10

    print(f"{'PLUGIN':{width_name}} {'STATE':{width_status}}")
    for k, v in plugin_dict.items():
        print(f"{k:{width_name}} {v:{width_status}}")


def get_file_name_extension(file_full_name: str) -> Tuple[str, List[str]]:
    "Get the name and the extensions of a file"
    file_path = Path(file_full_name)
    file_extensions: List[str] = file_path.suffixes
    file_name = file_full_name.replace("".join(file_extensions), "")
    return file_name, file_extensions


def install_plugin(plugin_file: str, plugin_dict: PluginDict) -> None:
    """Install third party plugins"""
    plugin_name, plugin_ext = get_file_name_extension(plugin_file)

    # Check if the plugin is present
    plugin_enable = "enabled"
    if plugin_name in plugin_dict.keys() and plugin_enable == plugin_dict[plugin_name]:
        print(f"plugin {plugin_name} is already installed in the system")
        return

    # Create the directory where the plugin is installed
    plugin_dir = Constants.plugins_work_area / plugin_name
    plugin_dir.mkdir(exist_ok=True)

    # Handle file's extensions
    if ".tar" in plugin_ext:
        with open_tar(plugin_file) as f:
            f.extractall(plugin_dir)
        print(f"plugin {plugin_file} was extracted successfully")

    # Update plugin dictionary
    plugin_dict[plugin_name] = plugin_enable
    print(f"plugin {plugin_name} was installed successfully")


def remove_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Remove third party plugins"""
    if plugin_name not in plugin_dict.keys():
        print(f"plugin {plugin_name} was not found in the system")
        return

    # Delete the directory where the plugin is installed
    plugin_dir = Constants.plugins_work_area / plugin_name
    rmtree(plugin_dir)

    del plugin_dict[plugin_name]
    print(f"plugin {plugin_name} was uninstalled successfully")


def enable_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Enable third party plugins"""
    plugin_enable = "enabled"
    if plugin_name in plugin_dict.keys() and plugin_enable == plugin_dict[plugin_name]:
        print(f"plugin {plugin_name} is already enabled in the system")
        return

    plugin_dict[plugin_name] = plugin_enable
    print(f"plugin {plugin_name} was enabled successfully")


def disable_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Disable third party plugins"""
    plugin_disable = "disabled"
    if plugin_name not in plugin_dict.keys():
        print(f"plugin {plugin_name} was not found in the system")
        return
    if plugin_disable == plugin_dict[plugin_name]:
        print(f"plugin {plugin_name} is already disabled in the system")
        return

    plugin_dict[plugin_name] = plugin_disable
    print(f"plugin {plugin_name} was disabled successfully")


def handle_plugins(args) -> None:
    """Handle third party plugins"""
    plugin_toml_file = Constants.plugins_work_area / "plugins.toml"
    plugin_data = load_toml(plugin_toml_file)
    plugin_dict = plugin_data["plugins"]

    if args.list:
        get_enabled_plugins()
        list_plugins(plugin_dict)
        return

    if args.install:
        install_plugin(args.install[0], plugin_dict)
    elif args.remove:
        remove_plugin(args.remove[0], plugin_dict)
    elif args.enable:
        enable_plugin(args.enable[0], plugin_dict)
    elif args.disable:
        disable_plugin(args.disable[0], plugin_dict)

    dump_toml(plugin_toml_file, plugin_data)


def set_plugin_subparser(subparsers) -> None:
    """create the parser for the 'plugin' command"""
    parser_plugin = subparsers.add_parser(
        "plugin", description="handle third party plugins"
    )
    group = parser_plugin.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--list", action="store_true", help="print the list of all plugins"
    )
    group.add_argument(
        "--install", type=validate_input, help="install a new plugin", nargs=1
    )
    group.add_argument("--remove", type=validate_input, help="remove a plugin", nargs=1)
    group.add_argument("--enable", type=validate_input, help="enable a plugin", nargs=1)
    group.add_argument(
        "--disable", type=validate_input, help="disable a plugin", nargs=1
    )
    parser_plugin.set_defaults(fn=handle_plugins)
