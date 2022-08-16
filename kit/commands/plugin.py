# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the usage of third party plug-ins"""


from kit.utils.subparsers import validate_input
from kit.utils.files import load_toml, dump_toml


def list_plugins(plugin_dict) -> None:
    """Print the list of all plug-ins"""
    width_plugin = max(map(len, plugin_dict.keys()), default=0) + 3
    width_status = 10

    print(f"{'PLUG-IN':{width_plugin}} {'STATE':{width_status}}")
    for k, v in plugin_dict.items():
        print(f"{k:{width_plugin}} {v:{width_status}}")


def install_plugin(plugin_name: str, plugin_dict: dict) -> None:
    """Install third party plug-in"""
    plugin_enable = "enabled"
    if plugin_name in plugin_dict.keys() and plugin_enable == plugin_dict[plugin_name]:
        print(f"Plug-in {plugin_name} is already installed in the system")
        return

    plugin_dict[plugin_name] = plugin_enable
    print(f"Plug-in {plugin_name} was installed successfully")


def remove_plugin(plugin_name: str, plugin_dict: dict) -> None:
    """Remove third party plug-ins"""
    plugin_disable = "disabled"
    if (
        plugin_name not in plugin_dict.keys()
        or plugin_disable == plugin_dict[plugin_name]
    ):
        print(f"Plug-in {plugin_name} was not found in the system")
        return

    plugin_dict[plugin_name] = plugin_disable
    print(f"Plug-in {plugin_name} was uninstalled successfully")


def handle_plugins(args) -> None:
    """handle third party plug-ins"""
    toml_file_key = "plugins"
    source_file = "~/.hekit/plugins/plugins.toml"
    plugin_data = load_toml(source_file)

    # case when the file is empty
    if toml_file_key not in plugin_data.keys():
        plugin_data[toml_file_key] = {}
    plugin_dict = plugin_data[toml_file_key]

    if args.list:
        list_plugins(plugin_dict)
    elif args.install:
        install_plugin(args.install[0], plugin_dict)
        dump_toml(source_file, plugin_data)
    elif args.remove:
        remove_plugin(args.remove[0], plugin_dict)
        dump_toml(source_file, plugin_data)


def set_plugin_subparser(subparsers) -> None:
    """create the parser for the 'plugin' command"""
    parser_plugin = subparsers.add_parser(
        "plugin", description="handle third party plug-ins"
    )
    group = parser_plugin.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--list", action="store_true", help="print the list of all plug-ins"
    )
    group.add_argument(
        "--install", type=validate_input, help="install a new plug-in", nargs=1
    )
    group.add_argument(
        "--remove", type=validate_input, help="remove a plug-in", nargs=1
    )
    parser_plugin.set_defaults(fn=handle_plugins)
