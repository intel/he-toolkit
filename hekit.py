#! /usr/bin/python3

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
import sys
import argparse

import os
import shutil
import pprint
from component_builder import ComponentBuilder, chain_run

repo_location = os.path.expanduser("~/.hekit")


def components_to_build_from(filename, category):
    """Returns a generator that yields a component to be built and/or installed"""
    toml_dict = toml.load(filename)
    category_objs = toml_dict[category]
    # Extracting specs also flattens 'list of list' to list
    specs = ((name, spec) for name, specs in category_objs.items() for spec in specs)

    return (
        ComponentBuilder(category, name, spec, repo_location) for name, spec in specs
    )


def install_components(args):
    """"""

    label = "dependency"
    # label = "library"
    components = components_to_build_from(args.install_file, label)

    for component in components:
        print(label)
        if component.skip():
            print(f"Skipping {label}")
            continue
        chain_run(
            [component.setup, component.fetch, component.build, component.install]
        )


def list_dirs(path: str):
    """Just return list of dirs in path."""
    _, dirs, _ = next(os.walk(path))
    return dirs


def list_components(args):
    """List to stdout info on components."""
    global repo_location
    # At the mo, just lists installed.
    width = 10
    print(f"{'component':{width}} {'instance':{width}} {'install':{width}}")

    for comp_name in sorted(list_dirs(repo_location)):
        comp_name_path = f"{repo_location}/{comp_name}"
        for comp_inst in sorted(list_dirs(comp_name_path)):
            try:
                info_filepath = f"{comp_name_path}/{comp_inst}/hekit.info"
                info_file = toml.load(info_filepath)
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{info_file['status']['install']:{width}}",
                )
            except FileNotFoundError:
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{'unknown':{width}}",
                    f"'{info_filepath}' not found",
                )
            except KeyError as emsg:
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{'unknown':{width}}",
                    f"key {emsg} not found",
                )


def remove_components(args):
    """"""
    try:
        component = args.component
        instance = args.instance
        path = f"{repo_location}/{component}/{instance}"
        shutil.rmtree(path)
        print(f"Instance '{instance}' of component '{component}' successfully removed")

    except FileNotFoundError:
        print(
            "Nothing to remove",
            f"Instance '{instance}' of component '{component}' not found.",
        )


def parse_cmds():
    """"""
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="PROG")
    parser.add_argument(
        "--version", action="store_true", help="display Intel HE toolit version"
    )
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
    parser_remove.add_argument("component", type=str, help="component to be removed")
    parser_remove.add_argument("instance", type=str, help="instance to be removed")
    parser_remove.set_defaults(fn=remove_components)

    return parser.parse_args()


def main():
    # Parse cmdline
    args = parse_cmds()

    if args.version:
        print("Intel HE Toolkit version 1.3.0")
        exit(0)

    # Run the command
    args.fn(args)


if __name__ == "__main__":
    main()
