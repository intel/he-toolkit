# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module generates a list of primes"""

from kit.utils.primes import write_primes


def set_gen_primes_subparser(subparsers):
    """Register subparser to generate primes"""

    parser = subparsers.add_parser(
        "gen-primes",
        description="generate primes in range [n, m] where n, m are positive integers",
    )
    parser.add_argument("start", type=int, default=2, help="start number")
    parser.add_argument("stop", type=int, default=100, help="stop number")
    parser.set_defaults(fn=gen_primes)


def gen_primes(args):
    """Generates a list of primes from start to stop values inclusive"""
    write_primes(args.start, args.stop)
