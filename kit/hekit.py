#! /usr/bin/python3

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
import sys
import argparse

import os
import shutil
from component_builder import ComponentBuilder, chain_run
from config import load_config


def components_to_build_from(filename, repo_location):
    """Returns a generator that yields a component to be built and/or installed"""
    components = toml.load(filename)
    # Extracting specs also flattens 'list of list' to list
    specs = ((name, spec) for name, specs in components.items() for spec in specs)

    return (ComponentBuilder(name, spec, repo_location) for name, spec in specs)


def install_components(args):
    """Install command"""
    repo_location = args.config.repo_location
    components = components_to_build_from(args.install_file, repo_location)

    for component in components:
        comp_label = f"{component.component_name()}/{component.instance_name()}"
        print(comp_label)
        if component.skip():
            print(f"Skipping", comp_label)
            continue
        chain_run(
            [component.setup, component.fetch, component.build, component.install]
        )


def list_dirs(path: str):
    """Return list of directories in path."""
    try:
        _, dirs, _ = next(os.walk(path))
        return dirs
    except StopIteration:
        return []


def list_components(args):
    """List to stdout info on components."""
    repo_location = args.config.repo_location
    # At the mo, just lists installed.
    width = 10
    print(
        f"{'component':{width}} {'instance':{width}} {'fetch':{width}} {'build':{width}} {'install':{width}}"
    )

    for comp_name in sorted(list_dirs(repo_location)):
        comp_name_path = f"{repo_location}/{comp_name}"
        for comp_inst in sorted(list_dirs(comp_name_path)):
            try:
                info_filepath = f"{comp_name_path}/{comp_inst}/hekit.info"
                info_file = toml.load(info_filepath)
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{info_file['status']['fetch']:{width}}",
                    f"{info_file['status']['build']:{width}}",
                    f"{info_file['status']['install']:{width}}",
                )
            except FileNotFoundError:
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"'{info_filepath}' not found",
                )
            except KeyError as emsg:
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"key {emsg} not found",
                )


def remove_components(args):
    """Remove component instances"""
    repo_location = args.config.repo_location
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


def parse_cmdline():
    """Parse commandline commands"""
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="hekit")
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

    return parser.parse_args(), parser.print_help


def main():

    toolkit_version = "2.0.0"
    args, print_help = parse_cmdline()

    # Load config file
    try:
        # replace the filename with the actual config
        args.config = load_config(args.config)
    except Exception as e:
        # Any exception from config file exit
        print(f"Error while parsing config file\n  {e!r}")
        exit(1)

    if args.version:
        print(f"Intel HE Toolkit version {toolkit_version}")
        exit(0)

    # Run the command
    if not hasattr(args, "fn"):
        print("hekit requires a command", file=sys.stderr)
        print_help(sys.stderr)
        exit(1)
    args.fn(args)


if __name__ == "__main__":
    main()
