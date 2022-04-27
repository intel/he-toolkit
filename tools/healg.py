#! /usr/bin/env python3

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module finds HE parameters based on user constraints"""

import sys

assert sys.version_info >= (3, 8)

import math
import re
import argparse
import subprocess  # nosec
from subprocess import CalledProcessError
import shutil
from functools import partial
from itertools import chain, combinations
from collections import Counter


def powerset(iterable):
    """Returns a generator.
       Note that we do not return the empty set.
       https://docs.python.org/3/library/itertools.html"""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))


def find_ms(ps, ds, factorize):
    """Generator returns the p, gen for max m's for p^d"""
    prime_factors = factorize(p ** d - 1 for p in ps for d in ds)
    if prime_factors:
        all_factors = tuple(powerset(primes) for primes in prime_factors)
        pd = ((p, d) for p in ps for d in ds)
        for (p, d), ms in zip(pd, all_factors):
            for m_factors in ms:
                yield p, d, m_factors


def str_to_range(s):
    """Parse a string and return a Python range object.
       This function expects a positive integer."""
    if s.isdigit():
        num = int(s)
        return range(num, num + 1)

    regex = re.compile(r"^((\d+)\s*-\s*(\d+))$")
    match = None
    try:
        match, start, end = regex.fullmatch(s).groups()
        if match is None:
            raise argparse.ArgumentTypeError(
                f"Unknown error. Range with match '{match}'"
            )
        start, end = int(start), int(end)
        if start > end:
            raise argparse.ArgumentTypeError(f"backward range '{match}'")
        return range(start, end + 1)
    except AttributeError as error:
        if match:
            raise argparse.ArgumentTypeError(
                f"Wrong syntax for range given '{match}'."
            ) from error
        raise argparse.ArgumentTypeError(
            f"Wrong syntax for range given '{s}'."
        ) from error


def parse_range(string, filter_fn=None):
    """Returns sorted list"""
    ranges = (str_to_range(s) for s in string.replace(" ", "").split(","))

    if filter_fn is None:
        unique_nums = {x for r in ranges for x in r}
    else:
        unique_nums = {x for r in ranges for x in r if filter_fn(x)}

    return sorted(unique_nums)


class PrimesFromFile:
    """Process primes from a text file."""

    def __init__(self, filename):
        """Load file with primes."""
        with open(filename, encoding="utf-8") as f:
            self.primes = tuple(int(p) for p in f.readlines())
            self.max = self.primes[-1]

    def is_prime(self, n):
        """Return True if prime for numbers upto numbers in the file."""
        if n > self.max:
            raise ValueError(f"Cannot process number higher than {self.max}")
        return n in self.primes


def parse_factor_line(line):
    """ 'num: f1 f2 f3' -> (num, (f1, f2, f3))"""
    split_line = line.split()  # ['key:', 'v1', 'v2' , ...]
    key = split_line[0]
    if key[-1] != ":":
        raise ValueError(f"{line} does not have valid key format")
    key = int(key[:-1])
    value = tuple(int(num) for num in split_line[1:])
    return key, value


def compute_prime_factors(numbers, factor_util="factor"):
    """Return generator. Keys m, Value prime factors.
       Process out to factor"""

    numbers = list(numbers)
    if len(numbers) == 0:
        return None

    command_and_args = [factor_util, *map(str, numbers)]

    try:
        out = subprocess.run(command_and_args, stdout=subprocess.PIPE, check=True)
    except CalledProcessError as error:
        # Was it a negative number on the input?
        if any(number < 0 for number in numbers):
            raise ValueError(
                f"A negative number was found in the input: {numbers}"
            ) from error
        raise error

    factor_lines = out.stdout.decode("ascii").strip().split("\n")

    # We only want the value a.k.a. the primes factors
    # A generator here does not save memory, but makes the parsing lazy
    return (parse_factor_line(line)[1] for line in factor_lines)


def parse_cmdline(argv: list = None):
    """Return parsed command line args"""

    primes_list = PrimesFromFile("primes.txt")

    parse_range_for_primes = partial(parse_range, filter_fn=primes_list.is_prime)

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "-p", type=parse_range_for_primes, default="2", help="Plaintext prime"
    )
    parser.add_argument(
        "-d", type=parse_range, default="1", help="Number of coefficients in a slot"
    )
    parser.add_argument(
        "--no-corrected", action="store_false", help="Include corrected d orders"
    )
    parser.add_argument(
        "--no-header", action="store_false", help="Do not print headers"
    )
    args = parser.parse_args(argv)

    if not args.p:
        print("prime p not found in numbers provided", file=sys.stderr)
        sys.exit(1)

    args.factor_util = shutil.which("factor") or shutil.which("gfactor")
    if args.factor_util is None:
        print("To run factor utility is required.", file=sys.stderr)
        sys.exit(1)

    return args


def phi(prime_factors):
    """"Euler's totient from prime factors.
        This function assumes that only primes are passed in."""
    c = Counter(prime_factors)
    return math.prod((p - 1) * p ** (k - 1) for p, k in c.items())


def correct_for_d(p, d, m):
    """Returns the minimum value of d satisfiying p^d = 1 mod m.
    Computations for valid ms with a starting point of p^d can
    sometimes lead to an erroneous d.

    This function expects that p is a prime number."""
    for e in range(1, d + 1):
        if (p ** e) % m == 1:
            break

    return e, e != d


def main(args):
    """Given a prime p(s) and a required d(s) what algebras (p, d, m)
    are available?"""

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


if __name__ == "__main__":
    args_main = parse_cmdline()
    main(args_main)
