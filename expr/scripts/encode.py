#!/usr/bin/env python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Encoder Program"""

import sys
import argparse
import math
from csv import DictReader
from pathlib import Path
from functools import partial
from itertools import zip_longest
from dataclasses import dataclass
from typing import List, Sequence, Iterable, Generator, Callable

from config import Config, ConfigError
from ptxt import Ptxt, Params


def int_to_poly(num: int, base: int, numof_coeffs: int) -> List[int]:
    """Return a list of coeffs of a polynomial encoded from an integer"""

    def coeffs(pd, num):
        for pth in pd:
            coeff, num = divmod(num, pth)
            yield coeff

    pd = (base ** i for i in reversed(range(numof_coeffs)))
    poly = list(coeffs(pd, num))
    if poly[0] >= base:
        raise ValueError(f"Integer cannot fit in {numof_coeffs} slot coeffs: {poly}")
    return poly


def inner_prod(vector_a: Sequence[int], vector_b: Sequence[int]) -> int:
    """Computes the inner product of two vectors"""
    if len(vector_a) != len(vector_b):
        raise ValueError(
            f"vector_a and vector_b are not the same length '{len(vector_a)} != {len(vector_b)}'"
        )
    return sum(a * b for a, b in zip(vector_a, vector_b))


class BaseFromAlphabet:
    def __init__(
        to_base: int, size: int, alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ) -> None:
        """Closure to do a change str to poly p base."""
        self.to_base = to_base
        self.size = size
        self.alphabet = alphabet

        self.len_alphabet = len(alphabet)
        if len_alphabet < 1:
            raise ValueError(
                f"Alphabet must have positive integer cardinality, not '{len_alphabet}'"
            )
        self.translation_table = {symbol: code for code, symbol in enumerate(alphabet)}

    def __call__(numstr: str) -> List[int]:
        # use table to convert to pivot base 10
        converted = [translation_table[c] for c in numstr]
        num_base_10 = inner_prod(
            converted, list(len_alphabet ** i for i in reversed(range(len(numstr))))
        )
        return int_to_poly(num_base_10, p=to_base, d=size)


# Itertools recipe https://docs.python.org/3.8/library/itertools.html
def grouper(iterable, n: int, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def transpose(ls: List, rows: int, cols: int) -> List:
    """Transpose list order. List ls is in column major.
       rows and cols are of the current layout in the list."""
    return [ls[c * rows + r] for r in range(rows) for c in range(cols)]


def read_txt_worth(data_list, nslots: int) -> Generator:
    """Reads up to a txt worth of entries (== number of slots) of """
    for txt_worth in grouper(data_list, nslots):
        yield [item for item in txt_worth if item is not None]


def composite_split(column: Iterable, subcols: int):
    """Generator splits a column into composite columns"""
    # column has many entries
    if subcols < 1:
        raise ValueError(
            f"Sub-columns must be an integer greater than 1, not {subcols}"
        )

    if subcols == 1:
        yield from column
        return

    for chars in column:
        len_chars = len(chars)
        chars_per_slot = math.ceil(len_chars / subcols)
        # Remember slices do not have out of bounds
        split_datum = [
            chars[i : i + chars_per_slot] for i in range(0, len_chars, chars_per_slot)
        ]
        split_datum.extend([""] * (subcols - len(split_datum)))
        yield from split_datum


def encode_datum(datum: str, policy_to_exec):
    """Encode a datum. The returned encoded datum is a list."""
    if isinstance(policy_to_exec, dict):
        # Translation table
        encoded_datum = [policy_to_exec[char] for char in datum]
    elif callable(policy_to_exec):
        # Assume function to be called to encode slot
        encoded_datum = policy_to_exec(datum)
    else:
        raise TypeError(f"Policy is not a dict or function: '{type(policy_to_exec)}'")
    return encoded_datum


def round_robin_encode(encode: Callable, data, composite_columns: int) -> List:
    """Encode data into composite lists. Uses a round robin approach.
    encode is a function used to encode one arg, a datum."""
    if composite_columns == 1:
        return [[encode(datum) for datum in data]]

    ptxt_data_list = [[] for _ in range(composite_columns)]
    for i, datum in enumerate(data):
        ptxt_data_list[i % composite_columns].append(encode(datum))
    return ptxt_data_list


def extend_with_repetitions(ls_of_ls: list, repeat: int) -> None:
    """Modifies lists"""
    if repeat == 1:
        return

    for ls in ls_of_ls:
        ls *= repeat  # NOTE objects are repeats not new objects


@dataclass(frozen=True)
class Policy:
    encode: str
    composite: int


class Encoder:
    """Encoder Base class"""

    def __init__(self, config: Config) -> None:
        # TODO policies need defining
        self.params: Params = config.params
        self.composite_columns: List[int] = config.composites
        self.column_policies: List[ColumnPolicies] = config.encodings
        self.repeat: int = config.segments  # segment divisor

    def __packing(self, ptxts: List[Ptxt]) -> None:
        """To be implemented by derived class"""
        raise NotImplemented

    def __call__(self, entries):
        """Encodes the entries. An entry is a dict with columns as attribs."""
        ptxts: List[Ptxt] = []
        for colname, policy in column_policies.items():
            exec_policy = policies[policy.encode]
            composite = policy.composite
            entries_by_column = (entry[colname] for entry in entries)
            column_data = composite_split(entries_by_column, composite)
            encode_datum_with_policy = partial(encode_datum, policy_to_exec=exec_policy)
            list_ptxt_data = round_robin_encode(
                encode_datum_with_policy, column_data, composite
            )
        self.__packing(ptxts)  # Will be either Client or Server
        # Note the above for server has list in column order, we need row order
        cols = sum(v.composite for v in column_policies.values())
        rows = math.ceil(len(entries) / repeat)
        return ptxts

    def base(numstr: str, from_base: int, to_base: int, size: int) -> List[int]:
        """Change a number in string to different base within finite size"""
        # Pivot to base 10 - python in does this for us upto base 36
        num_base10 = int(numstr, base=from_base)
        return int_to_poly(num_base10, p=to_base, d=size)


class ClientEncoder(Encoder):
    """Encoder for client"""

    def __packing(self, ptxts: List[Ptxt]) -> None:
        # TODO refactor so that padding is added maybe before encoding
        for ptxt_data in list_ptxt_data:
            # TODO surely, not required for each item
            padding_size_in_segment = (params.nslots // segment_divisor) - len(
                ptxt_data
            )
            if padding_size_in_segment < 0:
                max_queries = params.nslots // segment_divisor
                raise ValueError(
                    f"Cannot have '{len(ptxt_data)}' queries more than a segment allows '{max_queries}'"
                )
            ptxt_data.extend([] for _ in range(padding_size_in_segment))

        extend_with_repetitions(list_ptxt_data, repeat)
        ptxts.extend(
            Ptxt(self.params).insert_data(ptxt_data) for ptxt_data in list_ptxt_data
        )


class ServerEncoder(Encoder):
    """Encoder for server"""

    def __packing(self, ptxts: List[Ptxt]) -> None:
        # For the server, we must expand each datum into a ptxt.
        ptxts.extend(
            Ptxt(self.params).insert_repeated_across_slots(data)
            for ptxt_data in list_ptxt_data
            for data in grouper(ptxt_data, repeat, [])
        )

    def __call__(self, entries) -> List[Ptxt]:
        ptxts: List[Ptxt] = super.__call__(self, entries)
        return transpose(ptxts, rows, cols)


def how_many_entries_in_file(filename: str) -> int:
    """Return number of lines in a file."""
    with open(filename) as f:
        return sum(1 for _ in f)


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

    try:
        encode = (
            ServerEncoder(args.config)
            if args.server is True
            else ClientEncoder(args.config)
        )
        nslots = args.config.params.nslots
        segments = args.config.segments
        with open(args.datafile, newline="") as csvfile:
            csv_reader = DictReader(csvfile, delimiter=" ")
            for txt in read_txt_worth(csv_reader, nslots // segments):
                ptxts = encode(txt)
                for ptxt in ptxts:
                    print(ptxt.to_json(), file=fd)
    except FileNotFoundError as file_error:
        sys.stderr.write(f"{file_error!r}")
        sys.exit(1)
    except ConfigError as config_error:
        sys.stderr.write(f"{config_error}!r")
        sys.exit(1)


if __name__ == "__main__":
    cmdline_args = parse_args()
    main(cmdline_args)
