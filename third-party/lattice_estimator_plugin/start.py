# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


def set_lattice_estimator_subparser(subparsers):
    """create the parser for the lattice estimator plugin"""
    parser = subparsers.add_parser(
        "lattice-estimator", description="Albrecht et al.'s Lattice Estimator"
    )
    parser.add_argument(
        "--lang",
        metavar="language",
        type=str.upper,
        default="EN",
        choices=HelloWorlds.get_available_languages(),
        help="say hello world in this language",
    )
    parser.set_defaults(fn=TBA)
