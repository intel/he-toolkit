# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from kit.utils.component_builder import install_components_from_recipe_file
from pathlib import Path


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


def setup(args):
    """Setup the docker container to use the Lattice Estimator"""
    install_components_from_recipe_file(
        recipe_file="./recipes/install.toml",
        upto_stage="install",
        repo_location=Path("./test").resolve(),
        force=True,
        recipe_args=None,
    )


def run():
    """Takes user straight into the docker container"""
