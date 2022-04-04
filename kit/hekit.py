#! /usr/bin/env python3

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from os import geteuid
from sys import stderr
from argparse import ArgumentParser
from pathlib import Path

from config import load_config
from tab_completion import (
    enable_tab_completion,
    components_completer,
    instances_completer,
)

from command_init import init_hekit
from command_remove import remove_components
from command_list import list_components
from command_install import install_components
from command_check_deps import check_dependencies

try:
    # docker-py is optional and will not be used from within a docker container
    from command_docker_build import setup_docker
except ImportError as ie:

    def setup_docker(arg):  # pylint: disable=unused-argument
        print("This command is disabled. To enable it install the docker-py dependency")
        print("  pip install docker")


def get_recipe_arg_dict(recipe_arg: str):
    """Returns a dictionary filled with recipe_arg values"""
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

    # resolve first to follow the symlink, if any
    hekit_root_dir = Path(__file__).resolve().parent.parent

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
    parser_init.add_argument(
        "--default-config", action="store_true", help="setup default config file"
    )
    parser_init.set_defaults(fn=init_hekit, hekit_root_dir=hekit_root_dir)

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

    # create the parser for the "check-dependencies" command
    parser_check_dependencies = subparsers.add_parser(
        "check-dependencies", description="check system dependencies"
    )
    parser_check_dependencies.add_argument(
        "dependencies_file",
        metavar="dependencies-file",
        type=str,
        help="dependencies file",
    )
    parser_check_dependencies.set_defaults(fn=check_dependencies)

    # create the parser for the "docker-build" command
    parser_docker_build = subparsers.add_parser(
        "docker-build", description="docker build of the toolkit"
    )
    parser_docker_build.add_argument("--id", type=int, help="custom user and group id")
    parser_docker_build.add_argument(
        "--clean", action="store_true", help="delete staging"
    )
    # FIXME should this be its own subcommand?
    parser_docker_build.add_argument(
        "--check-only", action="store_true", help="only run container for proxy checks"
    )
    # In future change to accept several strings
    parser_docker_build.add_argument(
        "--enable",
        type=str,
        choices=["vscode"],
        help="add/enable extra features in docker build of toolkit",
    )
    parser_docker_build.add_argument(
        "-y", action="store_false", help="say yes to prompts"
    )
    parser_docker_build.set_defaults(fn=setup_docker, hekit_root_dir=hekit_root_dir)

    enable_tab_completion(parser)

    return parser.parse_args(), parser.print_help


def main():
    """"""
    args, print_help = parse_cmdline()

    if args.version:
        toolkit_version = "2.0.0"
        print(f"Intel HE Toolkit version {toolkit_version}")
        exit(0)

    # Load config file
    try:
        # FIXME logic convoluted here
        if args.fn != init_hekit:
            # replace the filename with the actual config
            args.config = load_config(args.config)
    except Exception as e:
        # Exit on any exception from config file
        print("Error while parsing config file\n", f"{e!r}", file=stderr)
        exit(1)

    # Run the command
    if args.fn is None:
        print("hekit requires a command", file=stderr)
        print_help(stderr)
        exit(1)
    args.fn(args)


if __name__ == "__main__":
    if geteuid() == 0:
        print("You cannot run hekit as root (a.k.a. superuser)")
        exit(1)

    main()
