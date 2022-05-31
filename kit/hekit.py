#! /usr/bin/env python3

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module is the main entry point to the hekit command and subcommands for
configuring the HE Toolkit environment
"""

import sys

assert sys.version_info >= (3, 8)

from os import geteuid, walk
from sys import stderr, exit as sys_exit
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from commands.init import init_hekit
from tools.healg import healg
from utils.constants import Constants  # pylint: disable=no-name-in-module
from utils.config import load_config  # pylint: disable=no-name-in-module
from utils.tab_completion import (  # pylint: disable=no-name-in-module
    enable_tab_completion,
)


def files_in_dir(path: str, cond) -> List[str]:
    """Returns a list of filenames in the directory given by path. Can be filtered by cond"""
    try:
        filenames = next(walk(path))[2]
        if cond is None:
            return filenames
        else:
            return list(filter(cond, filenames))
    except StopIteration:
        return []


def discover_subparsers_from(module_paths: List[str], root: str):
    """Import modules in module_paths, and discover and return a generator of set_.*_subparser functions"""
    for module_path in module_paths:
        filenames = files_in_dir(
            f"{root}/kit/{module_path}", lambda f: f[0] != "_" and f.endswith(".py")
        )
        imported_modules = (
            import_module(f"{module_path}.{fname[:-3]}") for fname in filenames
        )
        funcs = (
            (getattr(imported_module, funcname), funcname)
            for imported_module in imported_modules
            for funcname in dir(imported_module)
            if funcname.startswith("set_") and funcname.endswith("_subparser")
        )
        yield from funcs


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

    for func, name in discover_subparsers_from(["commands", "tools"], hekit_root_dir):
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

    # Load config file
    try:
        # FIXME logic convoluted here
        functions = [init_hekit, healg]
        if args.fn not in functions:  # pylint: disable=comparison-with-callable
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
