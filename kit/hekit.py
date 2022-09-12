# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module is the main entry point to the hekit command and subcommands for
configuring the HE Toolkit environment
"""

import sys

from os import geteuid
from sys import stderr, exit as sys_exit
from argparse import ArgumentParser,HelpFormatter
from pathlib import Path
from typing import Tuple

from kit.utils.subparsers import discover_subparsers_from, validate_input
from kit.utils.constants import Constants
from kit.utils.tab_completion import enable_tab_completion

if sys.version_info < (3, 8):
    print("Intel HE Toolkit requires Python version 3.8 or above", file=sys.stderr)
    sys_exit(1)


def parse_cmdline() -> Tuple:
    """Parse commandline commands"""

    # resolve first to follow the symlink, if any
    hekit_root_dir = Path(__file__).resolve().parent.parent

    formatter = lambda prog: HelpFormatter(prog,max_help_position=25)
    # create the top-level parser
    parser = ArgumentParser(prog="hekit",formatter_class=formatter)
    parser.set_defaults(fn=None)
    parser.add_argument(
        "--version", action="store_true", help="display Intel HE toolkit version"
    )
    parser.add_argument(
        "--config",
        type=validate_input,
        default="~/.hekit/default.config",
        help="use a non-default configuration file instead",
    )

    # create subparsers for each command
    subparsers = parser.add_subparsers(
    title="Sub Commands", description="Sub Commands List")


    for func in discover_subparsers_from(["commands", "tools"], hekit_root_dir / "kit"):
        try:
            func(subparsers)
        except TypeError:
            func(subparsers, hekit_root_dir)

    # try to enable tab completion
    enable_tab_completion(parser)

    return parser.parse_args(), parser.print_help


def main() -> None:
    """Starting point for program execution"""
    args, print_help = parse_cmdline()

    if args.version:
        print(f"Intel HE Toolkit version {Constants.version}")
        sys_exit(0)

    if args.fn is None:
        print("hekit requires a command", file=stderr)
        print_help(stderr)
        sys_exit(1)

    try:
        args.fn(args)  # Run the command
    except Exception as e:  # pylint: disable=broad-except
        print("Error while running subcommand\n", f"{e!r}", file=stderr)
        sys_exit(1)


if __name__ == "__main__":
    if geteuid() == 0:
        print("You cannot run hekit as root (a.k.a. superuser)")
        sys_exit(1)

    main()
