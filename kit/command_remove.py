# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from shutil import rmtree
from os import listdir
from tab_completion import components_completer, instances_completer


def remove_components(args):
    """Remove component instances"""
    repo_location = args.config.repo_location
    try:
        component = args.component
        instance = args.instance
        path = f"{repo_location}/{component}/{instance}"
        rmtree(path)
        print(f"Instance '{instance}' of component '{component}' successfully removed")

        # Delete the component directory if all its instances were deleted
        path = f"{repo_location}/{component}"
        if len(listdir(path)) == 0:
            rmtree(path)

    except FileNotFoundError:
        print(
            "Nothing to remove",
            f"Instance '{instance}' of component '{component}' not found.",
        )


def set_remove_subparser(subparsers):
    """create the parser for the 'remove' command"""
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
