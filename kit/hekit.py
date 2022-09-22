# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module is the main entry point to the hekit command and subcommands for
configuring the HE Toolkit environment
"""

import sys

from os import geteuid
from sys import stderr, exit as sys_exit
from argparse import ArgumentParser, HelpFormatter
from typing import Tuple

from kit.utils.subparsers import register_subparser
from kit.utils.constants import Constants
from kit.utils.tab_completion import enable_tab_completion

if sys.version_info < (3, 8):
    print("Intel HE Toolkit requires Python version 3.8 or above", file=sys.stderr)
    sys_exit(1)


def parse_cmdline() -> Tuple:
    """Parse commandline commands"""

    # create the top-level parser
    parser = ArgumentParser(
        prog="hekit",
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=25),
    )
    parser.set_defaults(fn=None)
    parser.add_argument(
        "--version", action="store_true", help="display Intel HE toolkit version"
    )

    # create subparsers for each command
    subparsers = parser.add_subparsers(
        title="Sub Commands", description="Sub Commands List"
    )
    register_subparser(subparsers)

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
