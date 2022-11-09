#!/usr/bin/env python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Decoder Program"""

import sys
import argparse
from itertools import islice
from functools import partial
from typing import Iterable, List, Optional, Tuple, Union

from ptxt import Ptxt
from config import Config
from natural import Natural


def sum_vectors(*vectors: Iterable[int]) -> List:
    """Return as list sum of vectors"""
    return [sum(elems) for elems in zip(*vectors)]


def sum_segments(slots, segment_divisor: int):
    """Returns a map object that segments the list of slots and return the sum."""
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
    num_cols: Union[int, str] = 1
    dims = header_line.split()
    len_dims = len(dims)
    if len_dims == 1:
        num_rows = dims[0]
    elif len_dims == 2:
        num_rows, num_cols = dims
    else:
        raise ValueError("Too many dimensions in header line")

    return int(num_rows), int(num_cols)


def parse_args(argv: Optional[List[str]] = None):
    """Parse argv either passed in or from cmdline"""
    parser = argparse.ArgumentParser(description="Decode result")
    parser.add_argument("datafile", type=str, help="data file to decode")
    parser.add_argument(
        "--config",
        type=partial(Config.from_toml, params_only=True),
        default="config.toml",
        help="set ptxt params and composite columns",
    )
    parser.add_argument(
        "--entries", type=Natural, default=0, help="number of ptxt input queries"
    )
    return parser.parse_args(argv) if argv else parser.parse_args()


def main(args):
    """Decoder Program"""
    try:
        with open(args.datafile, encoding="UTF-8", newline="") as jobjs:
            parse_header(jobjs.readline())  # first line not json
            ptxt = Ptxt(args.config.params)
            line_num = 1
            for jobj in jobjs:
                ptxt.from_json(jobj)
                summed_segments = sum_segments(ptxt.slots(), args.config.segments)
                for line_num, slot in enumerate(summed_segments, line_num):
                    if args.entries == 0 or line_num <= args.entries:
                        value = sum(slot)
                        if value == 1:
                            print(f"Match on line '{line_num}'")

                        if value > 1:
                            print(
                                f"Corruption line result '{line_num}' with slot '{slot}'"
                            )
    except ValueError as error:
        sys.stderr.write(f"{error!r}\n")
        sys.exit(1)


if __name__ == "__main__":
    cmdline_args = parse_args()
    main(cmdline_args)
