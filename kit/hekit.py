#! /usr/bin/python3

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import sys
import argparse

from config import load_config
from command_remove import remove_components
from command_list import list_components
from command_install import install_components


def parse_cmdline():
    """Parse commandline commands"""
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="hekit")
    parser.set_defaults(fn=None)
    parser.add_argument(
        "--version", action="store_true", help="display Intel HE toolit version"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="~/.hekit/default.config",
        help="use a non-default configuration file instead",
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # create the parser for the "list" command
    parser_list = subparsers.add_parser("list", help="lists installed components")
    parser_list.set_defaults(fn=list_components)

    # create the parser for the "install" command
    parser_install = subparsers.add_parser("install", help="installs components")
    parser_install.add_argument(
        "install_file",
        metavar="install-file",
        type=str,
        help="TOML file for installations",
    )
    parser_install.set_defaults(fn=install_components)

    # create the parser for the "remove" command
    parser_remove = subparsers.add_parser(
        "remove", help="removes/uninstalls components"
    )
    parser_remove.add_argument("component", type=str, help="component to be removed")
    parser_remove.add_argument("instance", type=str, help="instance to be removed")
    parser_remove.set_defaults(fn=remove_components)

    return parser.parse_args(), parser.print_help


def main():

    toolkit_version = "2.0.0"
    args, print_help = parse_cmdline()

    if args.version:
        print(f"Intel HE Toolkit version {toolkit_version}")
        exit(0)

    # Load config file
    try:
        # replace the filename with the actual config
        args.config = load_config(args.config)
    except Exception as e:
        # Exit on any exception from config file
        print(f"Error while parsing config file\n  {e!r}", file=sys.stderr)
        exit(1)

    # Run the command
    if args.fn is None:
        print("hekit requires a command", file=sys.stderr)
        print_help(sys.stderr)
        exit(1)
    args.fn(args)


if __name__ == "__main__":
    main()
