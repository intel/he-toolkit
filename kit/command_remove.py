# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module removes specific libraries"""

from shutil import rmtree
from os import listdir
from tab_completion import components_completer, instances_completer


def remove_components(args):
    """Remove component instances"""
    try:
        component = args.component
        instance = args.instance
        repo_path = args.config.repo_location
        comp_path = f"{repo_path}/{component}"
        inst_path = f"{comp_path}/{instance}"

        if args.all:
            if component or instance:
                raise ValueError(
                    "Flag '--all' cannot be used after specifying a component or instance"
                )

            value = input(
                f"All components in {repo_path} will be deleted. Do you want to continue? (y/n) "
            )
            if value in ("y", "Y"):
                rmtree(repo_path)
                print("All components successfully removed")
        elif not instance:
            value = input(
                f"All instances of component '{component}' will be deleted. Do you want to continue? (y/n) "
            )
            if value in ("y", "Y"):
                rmtree(comp_path)
                print(f"All instances of component '{component}' successfully removed")
        else:
            rmtree(inst_path)
            print(
                f"Instance '{instance}' of component '{component}' successfully removed"
            )

            # Delete the component directory if all its instances were deleted
            if len(listdir(comp_path)) == 0:
                rmtree(comp_path)

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
        "--all", action="store_true", help="remove all components"
    )
    parser_remove.add_argument(
        "component", type=str, help="component to be removed", nargs="?", default=""
    ).completer = components_completer
    parser_remove.add_argument(
        "instance", type=str, help="instance to be removed", nargs="?", default=""
    ).completer = instances_completer
    parser_remove.set_defaults(fn=remove_components)
