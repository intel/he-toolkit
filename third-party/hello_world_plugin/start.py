# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from hello_world_plugin.hello import print_msg


def set_hello_subparser(subparsers):
    """create the parser for the hello world plugin"""
    parser = subparsers.add_parser("hello_world_plugin", description="hello world")
    parser.add_argument("--quote", action="store_true", help="provide some quote")
    parser.set_defaults(fn=print_msg)
