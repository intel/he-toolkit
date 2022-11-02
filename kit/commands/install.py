# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module fetches, builds, or installs the requested libraries"""

from argparse import HelpFormatter
from pathlib import Path
from typing import Dict, Union
from kit.utils.component_builder import components_to_build_from, chain_run, stages
from kit.utils.subparsers import validate_input
from kit.utils.config import config_required


@config_required
def install_components(args):
    """Install command"""
    if Path(args.recipe_file).is_symlink():
        raise TypeError("The TOML file cannot be a symlink")

    the_stages = stages(args.upto_stage, args.force)

    components = components_to_build_from(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )

    for component in components:
        chain_run(the_stages(component))


def get_recipe_arg_dict(recipe_arg: str) -> Union[Dict[str, str], None]:
    """Returns a dictionary filled with recipe_arg values"""

    pairs = [pair.split("=") for pair in recipe_arg.replace(" ", "").split(",")]
    try:
        return dict(pairs)
    except ValueError as e:
        for pair in pairs:
            if len(pair) != 2:
                raise ValueError(f"Wrong format for {pair}. Expected key=value") from e
        return None


def set_install_subparser(subparsers) -> None:
    """create the parser for the 'install' command"""
    actions = ["install", "build", "fetch"]

    for action in actions:
        parser = subparsers.add_parser(
            action,
            description=f"{action} components",
            formatter_class=lambda prog: HelpFormatter(prog, max_help_position=30),
        )
        parser.add_argument(
            "recipe_file",
            metavar="recipe-file",
            type=validate_input,
            help=f"TOML file for {action}",
        )
        parser.add_argument(
            "--recipe_arg",
            default={},
            type=get_recipe_arg_dict,
            help="Collection of key=value pairs separated by commas. The content of the TOML file will be replaced with this data.",
        )

        if action == "fetch":
            parser.set_defaults(fn=install_components, upto_stage=action, force=False)
            return  # Don't include the rest

        parser.add_argument(
            "-f", "--force", action="store_true", help=f"Re-execute {action}"
        )
        parser.set_defaults(fn=install_components, upto_stage=action)
