#!/usr/bin/env python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Decoder Program"""


import sys
import argparse
from itertools import islice
from functools import reduce
from ptxt import Ptxt, read_params
from typing import List, Tuple


def sum_vectors(*vectors):
    """Return as list sum of vectors"""
    return [sum(elems) for elems in zip(*vectors)]


def sum_segments(slots, segment_divisor):
    """Returns a generator. Segment the list of slots and return the sum."""
    if segment_divisor < 1:
        raise ValueError(
            f"segment divisor must be a positive integer, not '{segment_divisor}'"
        )
    if segment_divisor == 1:
        return slots

    quot, rem = divmod(len(slots), segment_divisor)
    if rem != 0:
        raise ValueError(
            f"Segment divisor '{segment_divisor}' does not divide list length '{len(slots)}'"
        )

    segments = [islice(slots, i * quot, (i + 1) * quot) for i in range(segment_divisor)]

    return map(sum_vectors, *segments)


def parse_header(header_line: str) -> Tuple[int, int]:
    """Return the number of rows and columns from the header line"""
    num_cols = 1
    dims = header_line.split()
    if len(dims) == 1:
        num_rows = dims[0]
    elif len(dims) == 2:
        num_rows, num_cols = dims
    else:
        raise ValueError(f"Too many dimensions in header line")

    return int(num_rows), int(num_cols)


def parse_args(argv: List[str] = None):
    """Parse argv either passed in or from cmdline"""
    parser = argparse.ArgumentParser(description="Decode result")
    parser.add_argument("datafile", type=str, help="data file to decode")
    parser.add_argument("--params", type=str, help="parameters for encoding")
    parser.add_argument(
        "--segment", type=int, default=1, help="set segmentation divisor"
    )
    parser.add_argument(
        "--entries", type=int, default=0, help="number of input queries"
    )
    return parser.parse_args(argv) if argv else parser.parse_args()


def main(args):
    """Decoder Program"""

    params = read_params(args.params)
    if args.entries < 0:
        raise ValueError(
            f"Number of entries must be a positive integer, not '{args.entries}'"
        )

    with open(args.datafile, newline="") as f:
        # Read the dims
        # TODO use this info?
        num_rows, num_cols = parse_header(f.readline())
        ptxt = Ptxt(params)
        line_num = 1
        for jobj in f:
            ptxt.from_json(jobj)
            slots = ptxt.slots()
            for line_num, slot in enumerate(
                sum_segments(slots, args.segment), line_num
            ):
                if args.entries == 0 or line_num <= args.entries:
                    value = sum(slot)
                    if value == 1:
                        print(f"Match on line '{line_num}'")
                    elif value > 1:
                        print(f"Corruption line result '{line_num}' with slot '{slot}'")
                    else:
                        pass


if __name__ == "__main__":
    args = parse_args()
    main(args)
