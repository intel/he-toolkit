# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the usage of third party plugins"""


def handle_plugins(args) -> None:
    """handle third party plugins"""
    if args.list:
        print("List ")
    elif args.install:
        print("Install ")
    elif args.remove:
        print("Remove ")
    else:
        pass


def set_plugin_subparser(subparsers):
    """create the parser for the 'plugin' command"""
    parser_plugin = subparsers.add_parser(
        "plugin", description="handle third party plugins"
    )
    parser_plugin.add_argument(
        "--list", action="store_true", help="print the list of all plugins"
    )
    parser_plugin.add_argument(
        "--install", action="store_true", help="install a new plugin"
    )
    parser_plugin.add_argument("--remove", action="store_true", help="remove a plugin")
    parser_plugin.set_defaults(fn=handle_plugins)
