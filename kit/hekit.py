#! /usr/bin/env python3

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module is the main entry point to the hekit command and subcommands for
configuring the HE Toolkit environment
"""

from os import geteuid
from sys import stderr, exit as sys_exit
from argparse import ArgumentParser
from pathlib import Path

from config import load_config  # pylint: disable=no-name-in-module
from tab_completion import enable_tab_completion
from command_init import init_hekit, set_init_subparser
from command_remove import set_remove_subparser
from command_list import set_list_subparser
from command_install import set_install_subparser
from command_check_deps import set_check_dep_subparser
from tools.healg import set_gen_primes

try:
    # docker-py is optional and will not be used from within a docker container
    from command_docker_build import set_docker_subparser
except ImportError:

    def set_docker_subparser(arg1, arg2):  # pylint: disable=unused-argument
        """Informs that this command can't be used due to missing dependencies"""
        print("This command is disabled. To enable it install the docker-py dependency")
        print("  pip install docker")


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

    # create subparsers for each command
    subparsers = parser.add_subparsers(help="sub-command help")
    set_init_subparser(subparsers, hekit_root_dir)
    set_list_subparser(subparsers)
    set_install_subparser(subparsers)
    set_remove_subparser(subparsers)
    set_check_dep_subparser(subparsers)
    set_docker_subparser(subparsers, hekit_root_dir)
    set_gen_primes(subparsers)

    # try to enable tab completion
    enable_tab_completion(parser)

    return parser.parse_args(), parser.print_help


def main():
    """Starting point for program execution"""
    args, print_help = parse_cmdline()

    if args.version:
        toolkit_version = "2.0.0"
        print(f"Intel HE Toolkit version {toolkit_version}")
        sys_exit(0)

    # Load config file
    try:
        # FIXME logic convoluted here
        if args.fn != init_hekit:  # pylint: disable=comparison-with-callable
            # replace the filename with the actual config
            args.config = load_config(args.config)
    except Exception as e:  # pylint: disable=broad-except
        # Exit on any exception from config file
        print("Error while parsing config file\n", f"{e!r}", file=stderr)
        sys_exit(1)

    # Run the command
    if args.fn is None:
        print("hekit requires a command", file=stderr)
        print_help(stderr)
        sys_exit(1)
    args.fn(args)


if __name__ == "__main__":
    if geteuid() == 0:
        print("You cannot run hekit as root (a.k.a. superuser)")
        sys_exit(1)

    main()
