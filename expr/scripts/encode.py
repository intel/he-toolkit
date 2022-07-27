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
        "--server", action="store_true", help="Server encoding. Default is client."
    )
    parser.add_argument("--params", type=str, help="Parameters for encoding")
    parser.add_argument(
        "--config", type=Params.from_toml, default=None, help="set composite columns"
    )
    return parser.parse_args(argv) if argv else parser.parse_args()


def main(args) -> None:
    """Encoder Program"""

    encode = EncoderServer() if args.server is True else EncoderClient()
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
