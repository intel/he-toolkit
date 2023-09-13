# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Utils for computing things related to primes"""

from sys import stdout
from subprocess import CalledProcessError, run, PIPE  # nosec B404
from typing import Generator, Iterable


def parse_factor_line(line: str) -> tuple[int, tuple[int, ...]]:
    """'num: f1 f2 f3' -> (num, (f1, f2, f3))"""
    head, *tail = line.split()  # ['key:', 'v1', 'v2' , ...]
    if head[-1] != ":":
        raise ValueError(f"{line} does not have valid key format")
    key = int(head[:-1])  # exclude last char
    value = tuple(map(int, tail))
    return key, value


def compute_prime_factors(
    numbers: Iterable[int], factor_util: str = "factor"
) -> Generator:
    """Return generator. Keys m, Value prime factors.
    Process out to factor"""

    numbers = list(numbers)
    if len(numbers) == 0:
        raise ValueError("Input numbers is empty")

    command_and_args = [factor_util, *map(str, numbers)]
    try:
        out = run(command_and_args, stdout=PIPE, check=True)  # nosec B603
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


def write_primes(start: int, stop: int, outfile=stdout) -> None:
    """Writes to outfile a list of primes from start to stop values inclusive"""
    if start > stop:
        raise ValueError(f"start '{start}' should not be larger than stop '{stop}'")
    numbers = range(start, stop + 1)
    prime_factors = compute_prime_factors(numbers)
    if prime_factors is None:
        raise ValueError(
            f"No prime factors were found for between '{start}' and '{stop}', inclusively"
        )
    primes = [factors[0] for factors in prime_factors if len(factors) == 1]
    print("\n".join(map(str, primes)), file=outfile)
