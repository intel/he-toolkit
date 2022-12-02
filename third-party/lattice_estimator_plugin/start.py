# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from kit.utils.component_builder import install_components_from_recipe_file
from kit.utils.config import config_required


def set_lattice_estimator_subparser(subparsers):
    """create the parser for the lattice estimator plugin"""
    parser = subparsers.add_parser(
        "lattice-estimator", description="Albrecht et al.'s Lattice Estimator"
    )
    # TODO use proper subcommands
    parser.add_argument(
        "cmd",
        choices=("setup", "run"),
        help="",
    )
    parser.set_defaults(fn=setup)


@config_required
def setup(args):
    """"""
    install_components_from_recipe_file(
        "recipes/install.toml", "fetch", config.repo_location, force=False
    )


def run():
    """"""
