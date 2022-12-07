# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import sys
import subprocess
from kit.utils.component_builder import install_components_from_recipe_file

PLUGIN_ROOT = Path(".").resolve()


def set_lattice_estimator_subparser(subparsers) -> None:
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


def setup(args) -> None:
    """Setup the docker container to use the Lattice Estimator"""
    # Install a fresh copy of the lattice estimator
    install_components_from_recipe_file(
        recipe_file=PLUGIN_ROOT / "recipes/install.toml",
        upto_stage="fetch",
        repo_location=PLUGIN_ROOT / "test",
        force=True,
        recipe_args=None,
    )

    try:
        # Setup the docker container
        output = subprocess.run(["docker", "compose", "build"], capture_output=True)
        print(output)
    except PermissionError as error:
        print(
            f"{error}. Check that `docker` is installed and that you are part of the `docker` group",
            file=sys.stderr,
        )
        sys.exit(1)


def run(args) -> None:
    """Take the user straight into the docker container"""
