#!/usr/bin/env python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Encoder Program"""

import argparse
import csv
from pathlib import Path
from typing import List, Dict

from util import ClientEncoder, ServerEncoder, Params


def parse_args(argv: List[str] = None):
    """Parse argv either passed in or from the command line"""
    parser = argparse.ArgumentParser(description="Encoder for client and server sides")
    parser.add_argument("datafile", type=Path, help="Data file to encode")
    parser.add_argument(
        "--server",
        action="store_true",
        help="Server encoding. Default is client encoding.",
    )
    parser.add_argument(
        "--config",
        type=Config.from_toml,
        default=None,
        help="set ptxt params and composite columns",
    )
    return parser.parse_args(argv) if argv else parser.parse_args()


def main(args) -> None:
    """Encoder Program"""

    # TODO move to config obj
    # sanity check
    if args.config.params.nslots % args.config.segments != 0:
        sys.stderr.write(
            f"Segmentation divisor '{args.segment}' does not divide number of slots '{params.nslots}'"
        )
        exit(1)
    encode = (
        EncoderServer(args.config)
        if args.server is True
        else EncoderClient(args.config)
    )
    try:
        with open(args.datafile, newline="") as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=" ")
            for txt in read_txt_worth(csv_reader, params.nslots // args.segment):
                ptxts = encode(txt)
                for ptxt in ptxts:
                    print(ptxt.to_json(), file=fd)
    except FileNotFoundError:
        sys.stderr.write(f"Datafile '{args.datafile}' not found")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    main(args)
