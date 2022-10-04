# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module is the main entry point to the hekit command and subcommands for
configuring the HE Toolkit environment
"""

import sys

from os import geteuid
from sys import stderr, exit as sys_exit
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Tuple

from kit.utils.subparsers import (
    get_options_description,
    register_subparser,
    validate_input,
)
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
        description="execute Intel HE Toolkit commands",
        formatter_class=RawTextHelpFormatter,
    )
    parser.set_defaults(fn=None)
    parser.add_argument(
        "--debug", action="store_true", help="if exception occurs print out stacktrace"
    )
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
    subparsers = parser.add_subparsers(metavar="sub-command")
    register_subparser(subparsers)

    # Get the name and description for each sub-command
    subparsers.help = get_options_description(subparsers.choices, width=20)

    # try to enable tab completion
    enable_tab_completion(parser)

    return parser.parse_args(), parser.print_help


def main() -> None:
    """Starting point for program execution"""
    args, print_help = parse_cmdline()

    if args.version is True:
        print(f"Intel HE Toolkit version {Constants.version}")
        sys_exit(0)

    if args.fn is None:
        print("hekit requires a command", file=stderr)
        print_help(stderr)
        sys_exit(1)

    if args.debug is True:
        args.fn(args)
        sys_exit(0)

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
