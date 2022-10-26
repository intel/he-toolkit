#!/usr/bin/env python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import random
import toml
import sys
from pydantic import BaseModel, validator
from pathlib import Path
from typing import List, Union


class ColumnsDescription(BaseModel):
    """"""

    datatype: Union[str, List[str]]
    char_size: int

    # TODO add validators


def real_matches(filename: str, pick: int) -> List[str]:
    """Read in file and pick n lines at random. Return list."""
    with open(filename) as f:
        lines = list(f.readlines())  # Slurp file
    return random.sample(lines, pick)


def fake_rows(column_descriptions: List[ColumnsDescription]) -> str:
    """Generate fake entries."""


def main():
    """./datagen <columns_description> --total x
    ./datagen <columns_description> --total x --dbfile y --real z"""
    parser = argparse.ArgumentParser(description="Generate dummy data")
    parser.add_argument(
        "columns_description",
        metavar="column-description",
        type=str,
        help="description of columns",
    )
    parser.add_argument(
        "dbfile", nargs="?", type=str, help="data file to take real matches from"
    )
    parser.add_argument("--real", type=int, default=5, help="number of real matches")
    parser.add_argument("--total", type=int, default=10, help="total number of queries")
    args = parser.parse_args()

    tobj = toml.load(args.columns_description)

    # print column headers
    print(" ".join(tobj.keys()))

    columns_descriptions = [ColumnsDescription(**desc) for desc in tobj.values()]

    for row in fake_rows(columns_descriptions):
        print(row)

    return

    # sanity check
    diff = args.total - args.real
    if diff < 0:
        print(
            f"Number of chosen real matches '{args.real}' must not exceed total '{args.total}'",
            file=sys.stderr,
        )
        exit(1)

    queries = real_matches(args.dbfile, args.real)
    queries.extend(fake_queries(diff, args.digits))

    random.shuffle(queries)  # works in place

    for line in queries:
        print(line, end="")


if __name__ == "__main__":
    main()
