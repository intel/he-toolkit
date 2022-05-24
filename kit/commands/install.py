# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module fetches, builds, or installs the requested libraries"""

from typing import Dict
from utils.component_builder import (  # pylint: disable=no-name-in-module
    components_to_build_from,
    chain_run,
)


def _stages(upto_stage: str):
    """Return a generator"""
    if upto_stage not in ("fetch", "build", "install"):
        raise ValueError(f"Not a valid stage value '{upto_stage}'")

    def the_stages(component):
        yield component.setup
        yield component.fetch
        if upto_stage == "fetch":
            return
        yield component.build
        if upto_stage == "build":
            return
        yield component.install
        return

    return the_stages


def install_components(args):
    """Install command"""
    components = components_to_build_from(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )

    the_stages = _stages(args.upto_stage)

    for component in components:
        comp_label = f"{component.component_name()}/{component.instance_name()}"
        print(comp_label)
        if component.skip():
            print("Skipping", comp_label)
            continue

        chain_run(the_stages(component))


def get_recipe_arg_dict(recipe_arg: str) -> Dict[str, str]:
    """Returns a dictionary filled with recipe_arg values"""

    pairs = [pair.split("=") for pair in recipe_arg.replace(" ", "").split(",")]
    try:
        return dict(pairs)
    except ValueError as e:
        for pair in pairs:
            if len(pair) != 2:
                raise ValueError(f"Wrong format for {pair}. Expected key=value") from e
        return None


def set_install_subparser(subparsers):
    """create the parser for the 'install' command"""
    actions = ["install", "build", "fetch"]

    for action in actions:
        parser = subparsers.add_parser(action, description=f"{action} components")
        parser.add_argument(
            "recipe_file",
            metavar="recipe-file",
            type=str,
            help=f"TOML file for {action}",
        )
        parser.add_argument(
            "--recipe_arg",
            default={},
            type=get_recipe_arg_dict,
            help="Collection of key=value pairs separated by commas. The content of the TOML file will be replaced with this data.",
        )
        parser.set_defaults(fn=install_components, upto_stage=action)
