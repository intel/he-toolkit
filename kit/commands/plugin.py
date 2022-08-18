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
plugins_toml_file: Path = Constants.plugins_root_dir / "plugins.toml"
key_toml_file: str = "plugins"
plugin_enable: str = "enabled"
plugin_disable: str = "disabled"


def completer_plugins_enable(
    prefix, parsed_args, **kwargs
):  # pylint: disable=unused-argument
    """Return a list of plugins that are enabled"""
    return get_plugins_by_state()


def completer_plugins_disable(
    prefix, parsed_args, **kwargs
):  # pylint: disable=unused-argument
    """Return a list of plugins that are disabled"""
    return get_plugins_by_state(plugin_disable)


def get_plugins_by_state(state: str = plugin_enable):
    """Return a list of plugins with a specific state"""
    if plugins_toml_file.exists():
        plugin_dict = load_toml(plugins_toml_file)[key_toml_file]
        return [k for k, v in plugin_dict.items() if v == state]

    return []


def list_plugins(plugin_dict: PluginDict, state: str) -> None:
    """Print the list of all plugins"""
    width_name = max(map(len, plugin_dict.keys()), default=0) + 3
    width_status = 10

    print(f"{'PLUGIN':{width_name}} {'STATE':{width_status}}")
    for k, v in plugin_dict.items():
        if state in (v, "all"):
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
    if plugin_name in plugin_dict.keys() and plugin_enable == plugin_dict[plugin_name]:
        print(f"Plugin {plugin_name} is already installed in the system")
        return

    # Create the directory where the plugin is installed
    plugin_dir = Constants.plugins_root_dir / plugin_name
    plugin_dir.mkdir(exist_ok=True)

    # Handle file's extensions
    if ".tar" in plugin_ext:
        with open_tar(plugin_file) as f:
            f.extractall(plugin_dir)
        print(f"Plugin {plugin_file} was extracted successfully")

    # Update plugin dictionary
    plugin_dict[plugin_name] = plugin_enable
    print(f"Plugin {plugin_name} was installed successfully")


def remove_all_plugins(plugin_dict: PluginDict) -> None:
    """Remove all third party plugins"""
    for plugin_name in plugin_dict.keys():
        # Delete the directory where the plugin is installed
        plugin_path = Constants.plugins_root_dir / plugin_name
        if plugin_path.exists():
            rmtree(plugin_path)

    plugin_dict.clear()
    print("All Plugins were uninstalled successfully")


def remove_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Remove a specific third party plugins"""
    if plugin_name not in plugin_dict.keys():
        print(f"Plugin {plugin_name} was not found in the system")
        return

    # Delete the directory where the plugin is installed
    plugin_path = Constants.plugins_root_dir / plugin_name
    if plugin_path.exists():
        rmtree(plugin_path)

    del plugin_dict[plugin_name]
    print(f"Plugin {plugin_name} was uninstalled successfully")


def enable_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Enable third party plugins"""
    if plugin_name in plugin_dict.keys() and plugin_enable == plugin_dict[plugin_name]:
        print(f"Plugin {plugin_name} is already enabled in the system")
        return

    plugin_dict[plugin_name] = plugin_enable
    print(f"Plugin {plugin_name} was enabled successfully")


def disable_plugin(plugin_name: str, plugin_dict: PluginDict) -> None:
    """Disable third party plugins"""
    if plugin_name not in plugin_dict.keys():
        print(f"Plugin {plugin_name} was not found in the system")
        return
    if plugin_disable == plugin_dict[plugin_name]:
        print(f"Plugin {plugin_name} is already disabled in the system")
        return

    plugin_dict[plugin_name] = plugin_disable
    print(f"Plugin {plugin_name} was disabled successfully")


def handle_plugins(args) -> None:
    """Handle third party plugins"""
    if not plugins_toml_file.exists():
        print("Please execute: hekit init --default-config")
        return

    # Get the plugins data
    plugin_dict = load_toml(plugins_toml_file)[key_toml_file]

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
    sorted_plugin_dict = {key_toml_file: dict(sorted(plugin_dict.items()))}
    dump_toml(plugins_toml_file, sorted_plugin_dict)


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
        choices=["all", plugin_enable, plugin_disable],
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
    ).completer = completer_plugins_enable

    # enable options
    parser_enable = subparsers_plugin.add_parser(
        "enable", description="enable a plugin"
    )
    parser_enable.add_argument(
        "plugin_to_enable", type=validate_input, help="plugin name", metavar="PLUGIN"
    ).completer = completer_plugins_disable

    # disable options
    parser_disable = subparsers_plugin.add_parser(
        "disable", description="disable a plugin"
    )
    parser_disable.add_argument(
        "plugin_to_disable", type=validate_input, help="plugin name", metavar="PLUGIN"
    ).completer = completer_plugins_enable

    parser_plugin.set_defaults(fn=handle_plugins)
