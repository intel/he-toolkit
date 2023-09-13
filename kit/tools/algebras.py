# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module finds HE parameters based on user constraints"""

import math
import re
import shutil
from argparse import ArgumentTypeError
from sys import stderr, exit as sys_exit
from itertools import chain, combinations
from collections import Counter
from pathlib import Path
from typing import Callable, Generator, Iterable, Optional
from kit.utils.typing import PathType
from kit.utils.files import create_default_workspace
from kit.utils.primes import compute_prime_factors, write_primes


def powerset(iterable: Iterable[int]) -> chain:
    """Note that we do not return the empty set.
    https://docs.python.org/3/library/itertools.html"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


def find_ms(ps: Iterable[int], ds: Iterable[int], factorize: Callable) -> Generator:
    """Returns the p, gen for max m's for p^d"""
    prime_factors = factorize(p**d - 1 for p in ps for d in ds)
    if prime_factors:
        all_factors = tuple(powerset(primes) for primes in prime_factors)
        pd = ((p, d) for p in ps for d in ds)
        for (p, d), ms in zip(pd, all_factors):
            for m_factors in ms:
                yield p, d, m_factors


def str_to_range(s: str) -> range:
    """Parse a string and return a Python range object.
    This function expects a positive integer."""
    if s.isdigit():
        num = int(s)
        return range(num, num + 1)

    regex = re.compile(r"^((\d+)\s*-\s*(\d+))$")
    match = None
    try:
        fullmatch = regex.fullmatch(s)
        if fullmatch is None:
            raise ArgumentTypeError(f"Wrong syntax for range given '{s}'.")
        match, start, end = fullmatch.groups()
        if match is None:
            raise ArgumentTypeError(f"Unknown error. Range with match '{match}'")
        start, end = int(start), int(end)
        if start > end:
            raise ArgumentTypeError(f"backward range '{match}'")
        return range(start, end + 1)
    except AttributeError as error:
        if match:
            raise ArgumentTypeError(
                f"Wrong syntax for range given '{match}'."
            ) from error
        raise ArgumentTypeError(f"Wrong syntax for range given '{s}'.") from error


def parse_range(string: str, filter_fn: Optional[Callable] = None) -> list[int]:
    """Returns sorted list"""
    ranges = (str_to_range(s) for s in string.replace(" ", "").split(","))

    if filter_fn is None:
        unique_nums = {x for r in ranges for x in r}
    else:
        unique_nums = {x for r in ranges for x in r if filter_fn(x)}

    return sorted(unique_nums)


def parse_range_for_primes(string: str) -> list[int]:
    """Create a file with sorted primes"""
    default_primes_filepath = Path("~/.hekit/primes.txt").expanduser()
    try:
        primes_list = PrimesFromFile(default_primes_filepath)
    except FileNotFoundError:
        create_default_workspace()
        with default_primes_filepath.open("w", encoding="utf-8") as f:
            write_primes(2, 140_000, outfile=f)
        primes_list = PrimesFromFile(default_primes_filepath)

    return parse_range(string, filter_fn=primes_list.is_prime)


class PrimesFromFile:
    """Process primes from a text file."""

    def __init__(self, filename: PathType) -> None:
        """Load file with primes."""
        with open(filename, encoding="utf-8") as f:
            self.primes = tuple(int(p) for p in f.readlines())
            self.max = self.primes[-1]

    def is_prime(self, n: int) -> bool:
        """Return True if prime for numbers up to numbers in the file."""
        if n > self.max:
            raise ValueError(f"Cannot process number higher than {self.max}")
        return n in self.primes


def set_gen_algebras_subparser(subparsers) -> None:
    """Register subparser to generate algebras"""
    parser = subparsers.add_parser(
        "algebras", description="generate ZZ_p[x]/phi(X) algebras"
    )

    parser.add_argument(
        "-p", type=parse_range_for_primes, default="2", help="plaintext prime"
    )
    parser.add_argument(
        "-d", type=parse_range, default="1", help="number of coefficients in a slot"
    )
    parser.add_argument(
        "--no-corrected", action="store_false", help="include corrected d orders"
    )
    parser.add_argument(
        "--no-header", action="store_false", help="do not print headers"
    )

    factor_util = shutil.which("factor") or shutil.which("gfactor")
    if factor_util is None:
        print("To run, factor utility is required.", file=stderr)
        sys_exit(1)

    parser.set_defaults(fn=algebras, factor_util=factor_util)


def phi(prime_factors: Iterable[int]) -> int:
    """ "Euler's totient from prime factors.
    This function assumes that only primes are passed in."""
    c = Counter(prime_factors)
    return math.prod((p - 1) * p ** (k - 1) for p, k in c.items())


def correct_for_d(p: int, d: int, m: int) -> tuple[int, int]:
    """Returns the minimum value of d satisfiying p^d = 1 mod m.
    Computations for valid ms with a starting point of p^d can
    sometimes lead to an erroneous d (too large).

    This function expects that p is a prime number."""
    for e in range(1, d + 1):
        if (p**e) % m == 1:
            return e, e != d

    raise ValueError(
        f"exponent for p^e = 1 mod m, could not be found, (p, d, m) was ({p}, {d}, {m})"
    )


def algebras(args):
    """Given a prime p(s) and a required d(s) what algebras (p, d, m)
    are available?"""

    # Sanity check that we have at least one prime to work with
    if not args.p:
        print("prime p not found in numbers provided", file=stderr)
        sys_exit(1)

    solns = set()
    width = 20
    if args.no_header:
        print(
            f"{'p' :^{width}} {'d' :^{width}} {'m' :^{width}} {'phim' :^{width}} {'nslots' :^{width}}"
        )
    for p, d, m_factors in find_ms(args.p, args.d, compute_prime_factors):
        m = math.prod(m_factors)
        e, corrected = correct_for_d(p, d, m)
        soln = (p, e, m)
        if soln not in solns:
            solns.add(soln)
            if not args.no_corrected and corrected:
                continue
            phim = phi(m_factors)
            print(
                f"{p :^{width}} {e :^{width}} {m :^{width}} {phim :^{width}} {phim // e :^{width}}"
            )

    if args.no_header:
        print(
            f"{'p' :^{width}} {'d' :^{width}} {'m' :^{width}} {'phim' :^{width}} {'nslots' :^{width}}"
        )
