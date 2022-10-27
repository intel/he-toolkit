#!/usr/bin/env python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Simple program to generate dummy data for configurable PSI"""

from __future__ import annotations

import argparse
import random
import sys
import string
from typing import Generator, List, Union

import toml
from pydantic import BaseModel, validator


class ColumnsDescription(BaseModel):
    """Description on columns to generate."""

    datatype: Union[str, List[str]]
    char_size: int = 1

    # @validator("datatype")
    # def _set_known_collections(cls, collection):

    @validator("datatype")
    def _set_known_collections(
        cls, collection: Union[str, List[str]]
    ) -> Union[str, List[str]]:
        """Converts known collection names to the collections themselves."""
        if isinstance(collection, list):
            return collection
        if collection == "alphabetic":
            return string.ascii_letters[26:]
        if collection == "alphanumeric":
            return string.ascii_letters[26:] + string.digits
        if collection == "numeric":
            return string.digits

        raise ValueError(f"Unknown collection name '{collection}'")

    @validator("char_size")
    def _greater_than_or_equal_to_one(cls, size: int):
        """check size is greater than or equal to one"""
        if size < 1:
            raise ValueError(f"size must be greater than or equal to one: '{size}'")
        return size


def real_matches(filename: str, pick: int) -> List[str]:
    """Read in file and pick n lines at random. Return list."""
    with open(filename, encoding="utf-8") as fstrm:
        fstrm.readline()  # ignore header
        lines = [line.strip() for line in fstrm.readlines()]  # slurp file
    return random.sample(lines, pick)


def fake_rows(column_descriptions: List[ColumnsDescription], rows: int) -> Generator:
    """Generate fake entries."""

    def column(collection, size):
        return "".join(random.choices(collection, k=size))  # nosec B311

    return (
        " ".join(column(desc.datatype, desc.char_size) for desc in column_descriptions)
        for _ in range(rows)
    )


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
    columns_descriptions = [ColumnsDescription(**desc) for desc in tobj.values()]

    # print column headers
    print(" ".join(tobj.keys()))

    if args.dbfile is None:
        for row in fake_rows(columns_descriptions, args.total):
            print(row)
        sys.exit(0)

    # sanity check
    diff = args.total - args.real
    if diff < 0:
        print(
            f"Number of chosen real matches '{args.real}' must not exceed total '{args.total}'",
            file=sys.stderr,
        )
        sys.exit(1)

    queries = real_matches(args.dbfile, args.real)
    queries.extend(fake_rows(columns_descriptions, diff))
    random.shuffle(queries)  # works in place

    for line in queries:
        print(line)


if __name__ == "__main__":
    main()
