#!/usr/bin/env python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Encoder Program"""

import argparse
from typing import List, Dict


def load_toml(arg: str) -> Dict:
    """"""


def parse_args(argv: List[str] = None):
    """Parse argv either passed in or from the command line"""
    parser = argparse.ArgumentParser(description="Encoder for client and server sides")
    parser.add_argument("datafile", type=str, help="data file to encode")
    parser.add_argument("--params", type=str, help="parameters for encoding")
    parser.add_argument(
        "--config", type=load_toml, default=None, help="set composite columns"
    )
    return parser.parse_args(argv) if argv else parser.parse_args()


def main(args) -> None:
    """"""


if __name__ == "__main__":
    args = parse_args()
    main(args)
