# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the usage of third party plugins"""

from shutil import rmtree, unpack_archive, get_archive_formats
from typing import Dict
from kit.utils.constants import PluginsConfig, PluginState
from kit.utils.files import load_toml, dump_toml, file_exists, get_file_name
from kit.utils.subparsers import validate_input
from kit.utils.tab_completion import plugins_enable_completer, plugins_disable_completer


PluginDict = Dict[str, str]


def list_plugins(plugin_dict: PluginDict, state: str) -> None:
    """Print the list of all plugins"""
    width_name = max(map(len, plugin_dict.keys()), default=0) + 3
    width_status = 10

    print(f"{'PLUGIN':{width_name}} {'STATE':{width_status}}")
    for k, v in plugin_dict.items():
        if state in (v, "all"):
            print(f"{k:{width_name}} {v:{width_status}}")


def install_plugin(plugin_file: str, plugin_dict: PluginDict) -> None:
    """Install third party plugins"""
    plugin_name = get_file_name(plugin_file)

    # Check if the plugin is present
    if (
        plugin_name in plugin_dict.keys()
        and PluginState.ENABLE == plugin_dict[plugin_name]
    ):
        print(f"Plugin {plugin_name} is already installed in the system")
        return

    # Create the directory where the plugin is installed
    plugin_dir = PluginsConfig.ROOT_DIR / plugin_name
    plugin_dir.mkdir(exist_ok=True)

    try:
        unpack_archive(plugin_file, plugin_dir)
        print(f"Plugin {plugin_file} was extracted successfully")
    except Exception as e:
        valid_formats = ", ".join([ext for ext, _ in get_archive_formats()])
        raise TypeError(
            f"{plugin_file} is not valid file. Supported formats are: {valid_formats}"
        ) from e

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
