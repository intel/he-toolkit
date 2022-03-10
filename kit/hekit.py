#! /usr/bin/env python3

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from sys import stderr
from argparse import ArgumentParser
from pathlib import Path

from config import load_config
from command_init import init_hekit
from command_remove import remove_components
from command_list import list_components
from command_install import install_components
from tab_completion import (
    enable_tab_completion,
    components_completer,
    instances_completer,
)


def get_recipe_arg_dict(recipe_arg: str):
    """Returns a dictionary filled with recipe_arg values"""
    # Case when recipe_arg was not defined
    if not isinstance(recipe_arg, str):
        return {}

    # Fill the dict if the user defined recipe_arg
    recipe_arg_dict = {}

    for pair in recipe_arg.replace(" ", "").split(","):
        key_value = pair.split("=")

        if len(key_value) != 2:
            raise ValueError(f"Wrong format for {key_value}. Expected key=value")

        key, value = key_value
        recipe_arg_dict[key] = value

    return recipe_arg_dict


def parse_cmdline():
    """Parse commandline commands"""
    # create the top-level parser
    parser = ArgumentParser(prog="hekit")
    parser.set_defaults(fn=None)
    parser.add_argument(
        "--version", action="store_true", help="display Intel HE toolkit version"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="~/.hekit/default.config",
        help="use a non-default configuration file instead",
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # create the parser for the "init" command
    parser_init = subparsers.add_parser("init", description="initialize hekit")
    parser_init.set_defaults(
        # resolve first to follow the symlink, if any
        fn=init_hekit,
        hekit_root_dir=Path(__file__).resolve().parent.parent,
    )

    # create the parser for the "list" command
    parser_list = subparsers.add_parser(
        "list", description="lists installed components"
    )
    parser_list.set_defaults(fn=list_components)

    # create the parser for the "install" command
    parser_install = subparsers.add_parser("install", description="installs components")
    parser_install.add_argument(
        "recipe_file", metavar="recipe-file", type=str, help="TOML file for install"
    )
    parser_install.add_argument(
        "--recipe_arg",
        default={},
        type=get_recipe_arg_dict,
        help="Collection of key=value pairs separated by commas. The content of the TOML file will be replaced with this data",
    )
    parser_install.set_defaults(fn=install_components, upto_stage="install")

    # create the parser for the "build" command
    parser_build = subparsers.add_parser("build", description="builds components")
    parser_build.add_argument(
        "recipe_file", metavar="recipe-file", type=str, help="TOML file for build"
    )
    parser_build.add_argument(
        "--recipe_arg",
        default={},
        type=get_recipe_arg_dict,
        help="Collection of key=value pairs separated by commas. The content of the TOML file will be replaced with this data",
    )
    parser_build.set_defaults(fn=install_components, upto_stage="build")

    # create the parser for the "fetch" command
    parser_fetch = subparsers.add_parser("fetch", description="fetches components")
    parser_fetch.add_argument(
        "recipe_file", metavar="recipe-file", type=str, help="TOML file for fetch"
    )
    parser_fetch.add_argument(
        "--recipe_arg",
        default={},
        type=get_recipe_arg_dict,
        help="Collection of key=value pairs separated by commas. The content of the TOML file will be replaced with this data",
    )
    parser_fetch.set_defaults(fn=install_components, upto_stage="fetch")

    # create the parser for the "remove" command
    parser_remove = subparsers.add_parser(
        "remove", description="removes/uninstalls components"
    )
    parser_remove.add_argument(
        "component", type=str, help="component to be removed"
    ).completer = components_completer
    parser_remove.add_argument(
        "instance", type=str, help="instance to be removed"
    ).completer = instances_completer
    parser_remove.set_defaults(fn=remove_components)

    enable_tab_completion(parser)

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
        print(f"Error while parsing config file\n  {e!r}", file=stderr)
        exit(1)

    # Run the command
    if args.fn is None:
        print("hekit requires a command", file=stderr)
        print_help(stderr)
        exit(1)
    args.fn(args)


if __name__ == "__main__":
    main()
