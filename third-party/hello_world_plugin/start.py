# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from hello_world.hello import HelloWorlds


def set_hello_subparser(subparsers):
    """create the parser for the hello world plugin"""
    parser = subparsers.add_parser("hello-world", description="hello world")
    parser.add_argument(
        "--lang",
        metavar="language",
        type=str.upper,
        default="EN",
        choices=HelloWorlds.get_available_languages(),
        help="say hello world in this language",
    )
    parser.set_defaults(fn=HelloWorlds.print_msg)
