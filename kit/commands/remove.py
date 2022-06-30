# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module removes specific libraries"""

from shutil import rmtree
from os import listdir
from kit.utils.tab_completion import components_completer, instances_completer
from kit.utils.subparsers import validate_input


def remove_components(args):
    """Remove component instances"""
    try:
        user_answer = "y"
        request_info = args.y
        component = args.component
        instance = args.instance
        repo_path = args.config.repo_location
        comp_path = f"{repo_path}/{component}"
        inst_path = f"{comp_path}/{instance}"

        if args.all:
            # Case: delete all components
            if component or instance:
                raise ValueError(
                    "Flag '--all' cannot be used when specifying a component or instance"
                )
            if request_info:
                user_answer = input(
                    f"All components in {repo_path} will be deleted. Do you want to continue? (y/n) "
                )
            if user_answer in ("y", "Y"):
                rmtree(repo_path)
                print("All components successfully removed")
        elif not component:
            raise ValueError(
                "A component or flag '--all' should be specified as argument"
            )
        elif not instance:
            # Case: delete all instances of a component
            if request_info:
                user_answer = input(
                    f"All instances of component '{component}' will be deleted. Do you want to continue? (y/n) "
                )
            if user_answer in ("y", "Y"):
                rmtree(comp_path)
                print(f"All instances of component '{component}' successfully removed")
        else:
            # Case: delete a specific instances of a component
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
    parser_remove.add_argument("-y", action="store_false", help="say yes to prompts")
    parser_remove.add_argument(
        "component",
        type=validate_input,
        help="component to be removed",
        nargs="?",
        default="",
    ).completer = components_completer
    parser_remove.add_argument(
        "instance",
        type=validate_input,
        help="instance to be removed",
        nargs="?",
        default="",
    ).completer = instances_completer
    parser_remove.set_defaults(fn=remove_components)
