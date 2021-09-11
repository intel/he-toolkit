#! /usr/bin/python3

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
import sys
import argparse

import os
import pprint
from component_builder import ComponentBuilder, chain_run

repo_location = os.path.expanduser("~/.hekit")


def components_to_build_from(filename, category):
    """Returns a generator that yields a component to be built and/or installed"""
    toml_dict = toml.load(filename)
    category_objs = toml_dict[category]
    # Extracting specs also flattens 'list of list' to list
    specs = (
        specs
        for name, category_specs in category_objs.items()
        for specs in category_specs
    )
    return (ComponentBuilder(spec) for spec in specs)


def install_components(args):
    """"""

    label = "dependency"
    # label = "libraries"
    components = components_to_build_from(args.install_file, label)

    for component in components:
        print(label)
        chain_run(
            [
                component.fetch,
                component.pre_build,
                component.build,
                component.post_build,
                component.install,
            ]
        )


def list_dirs(path: str):
    """Just return list of dirs in path."""
    _, dirs, _ = next(os.walk(path))
    return dirs


def list_components(args):
    """List to stdout info on components."""
    global repo_location
    # At the mo, just lists installed.
    root = f"{repo_location}/installs"
    for dir in sorted(list_dirs(root)):
        try:
            info_filepath = f"{root}/{dir}/hekit.info"
            info_file = toml.load(info_filepath)
            print(dir, info_file["status"])
        except FileNotFoundError:
            print(dir, "unknown", f"'{info_filepath}' not found")
        except KeyError as emsg:
            print(dir, "unknown", f"key {emsg} not found")


def remove_components(args):
    """"""


def parse_cmds():
    """"""
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="PROG")
    #    parser.add_argument('--foo', action='store_true', help='foo help')
    subparsers = parser.add_subparsers(help="sub-command help")

    # create the parser for the "list" command
    parser_list = subparsers.add_parser("list", help="lists installed components")
    #    parser_list.add_argument('bar', type=int, help='bar help')
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
    #    parser_remove.add_argument('--baz', choices='XYZ', help='baz help')
    parser_remove.set_defaults(fn=remove_components)

    return parser.parse_args()


def main():
    # Parse cmdline
    args = parse_cmds()

    # Run the command
    args.fn(args)

    print(args)


if __name__ == "__main__":
    main()
