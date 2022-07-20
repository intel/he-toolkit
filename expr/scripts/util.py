# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Encoder utility functions"""

from itertools import zip_longest
from typing import List, Sequence


def int_to_pd_poly(num: int, base: int, no_coeffs: int) -> List[int]:
    """Return a list of coeffs of a polynomial encoded from an integer"""

    def coeffs(pd, num):
        for pth in pd:
            coeff, num = divmod(num, pth)
            yield coeff

    pd = (base ** i for i in reversed(range(no_coeffs)))
    poly = list(coeffs(pd, num))
    if poly[0] >= p:
        raise ValueError(f"Integer cannot fit in {d} slot coeffs: {poly}")
    return poly


def inner_prod(vector_a: Sequence[int], vector_b: Sequence[int]) -> int:
    """Computes the inner product of two vectors"""
    if len(vector_a) != len(vector_b):
        raise ValueError(
            f"vector_a and vector_b are not the same length '{len(vector_a)} != {len(vector_b)}'"
        )
    return sum(a * b for a, b in zip(vector_a, vector_b))


def BaseFromAlphabet(to_base, size, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """Closure to do a change str to poly p base."""
    len_alphabet = len(alphabet)
    if len_alphabet < 1:
        raise ValueError(
            f"Alphabet must have positive integer cardinality, not '{len_alphabet}'"
        )
    translation_table = {symbol: code for code, symbol in enumerate(alphabet)}

    def _base_from_alphabet(numstr):
        # use table to convert to pivot base 10
        converted = [translation_table[c] for c in numstr]
        num_base_10 = inner_prod(
            converted, list(len_alphabet ** i for i in reversed(range(len(numstr))))
        )
        return int_to_pd_poly(num_base_10, p=to_base, d=size)

    return _base_from_alphabet


def base(numstr: str, from_base: int, to_base: int, size: int):
    """Change a number in string to different base within finite size"""
    # Pivot to base 10 - python in does this for us upto base 36
    num_base10 = int(numstr, base=from_base)
    return int_to_pd_poly(num_base10, p=to_base, d=size)


# This is from a itertools recipe
# https://docs.python.org/3.8/library/itertools.html
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def transpose(ls: list, rows: int, cols: int):
    """Transpose list order. List ls is in column major.
       rows and cols are of the current layout in the list."""
    return [ls[c * rows + r] for r in range(rows) for c in range(cols)]
