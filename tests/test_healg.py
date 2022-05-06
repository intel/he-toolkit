# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import subprocess
import os.path
from sys import maxsize
from argparse import ArgumentTypeError

from .context import healg
from healg import *


def test_powerset():
    # Check that empty set is not returned
    assert len(list(powerset([]))) == 0
    assert len(list(powerset([0]))) == 1

    assert list(powerset("AB")) == [("A",), ("B",), ("A", "B")]
    assert list(powerset([2, 2])) == [(2,), (2,), (2, 2)]
    assert len(list(powerset(range(3)))) == 7
    assert len(list(powerset({-1, -2, 0, 3}))) == 15

    with pytest.raises(TypeError):
        powerset(1)


def test_prime_factors():
    assert len(list(compute_prime_factors([x for x in range(10)]))) == 10
    assert list(compute_prime_factors([1])) == [()]  # Special case
    assert list(compute_prime_factors([5])) == [(5,)]
    assert list(compute_prime_factors([12])) == [(2, 2, 3)]
    # Note that largest prime pre-computed in primes.txt is 139999
    assert set(compute_prime_factors([24, 10009729])) == set(
        [(2, 2, 2, 3), (10009729,)]
    )

    # cmdline factor util hangs with no input
    # compute_prime_factors should not hang if no input passed in
    assert compute_prime_factors([]) is None

    with pytest.raises(ValueError):
        list(compute_prime_factors([-1]))

    with pytest.raises(CalledProcessError):
        list(compute_prime_factors([7.5]))


def test_find_ms():
    assert list(find_ms(ps=[], ds=[], factorize=compute_prime_factors)) == []
    assert set(find_ms([12], [5], compute_prime_factors)) == set(
        [(12, 5, (11,)), (12, 5, (22621,)), (12, 5, (11, 22621))]
    )
    assert set(find_ms([2, 3], [2, 3], compute_prime_factors)) == set(
        [
            (2, 2, (3,)),
            (2, 3, (7,)),
            (3, 2, (2,)),
            (3, 2, (2,)),
            (3, 2, (2,)),
            (3, 2, (2, 2)),
            (3, 2, (2, 2)),
            (3, 2, (2, 2)),
            (3, 2, (2, 2, 2)),
            (3, 3, (2,)),
            (3, 3, (13,)),
            (3, 3, (2, 13)),
        ]
    )

    with pytest.raises(TypeError):
        list(find_ms(12, 1, compute_prime_factors))

    with pytest.raises(CalledProcessError):
        # Checking for positive integers
        list(find_ms([8.5], [1], compute_prime_factors))
        list(find_ms([4], [1.5], compute_prime_factors))
        list(find_ms([12], [-1], compute_prime_factors))
        list(find_ms([-12], [1], compute_prime_factors))


def test_phi():
    assert phi([0]) == -1
    assert phi([1]) == 0
    assert phi([9]) == 8
    assert phi([2, 2, 3]) == 4
    assert phi([2, 2, 5]) == 8

    with pytest.raises(TypeError):
        assert phi(0)
        assert phi([[2], [3]])


def test_correct_for_d():
    # FIXME What to do about a p that is not prime?
    # assert correct_for_d(1, 3, 2) == (1, True)
    assert correct_for_d(p=2, d=8, m=15) == (4, True)
    assert correct_for_d(2, 3, 2) == (3, False)
    assert correct_for_d(3, 5, 3) == (5, False)

    # correct_for_d() expects that p=prime number
    # but does not explicitly check for it.
    # If non-prime passed in, correct functionality
    # is to still execute
    assert correct_for_d(4, 7, 3) == (1, True)
    assert correct_for_d(4, 2, 4) == (2, False)

    with pytest.raises(ZeroDivisionError):
        correct_for_d(1, 3, 0)

    with pytest.raises(UnboundLocalError):
        correct_for_d(2, 0, 5)


def test_str_to_range():
    # Test single digit parsing
    assert type(str_to_range("10")) == range
    assert len([x for x in str_to_range("100")]) == 1
    assert [x for x in str_to_range("0")] == [0]
    # In Python3, there is technically no limit or max val for an integer
    assert [x for x in str_to_range(str(maxsize + 1))] == [maxsize + 1]

    # Test range parsing
    assert [x for x in str_to_range("3-5")] == [x for x in range(3, 6)]

    white_space_test = [x for x in str_to_range("900 \t -  9999")]
    assert len(white_space_test) == 9100
    assert white_space_test[0] == 900 and white_space_test[-1] == 9999

    with pytest.raises(ArgumentTypeError):
        str_to_range("10.01")
        str_to_range("-101")
        str_to_range(str(float("inf")))
        str_to_range("abc")

        str_to_range("1000-999")
        str_to_range("ab-bc")


def test_parse_range():
    assert type(parse_range("0")) == list
    assert parse_range("3,5,4") == [3, 4, 5]  # check if sorted
    assert parse_range("100, 4, " + str(maxsize)) == [4, 100, maxsize]
    assert parse_range("0-10") == [x for x in range(0, 11)]
    assert len(parse_range("10 \t - \t 20")) == 11

    with pytest.raises(ArgumentTypeError):
        parse_range("-1")
        parse_range("10**3")
        parse_range("-1-20")


@pytest.fixture
def primes_file_obj(tmp_path):
    # a primes.txt needs to be generated for testing
    # check tools first to see if file exists
    f_primes = tmp_path / "primes.txt"

    with f_primes.open("w") as f:
        gen_primes(2, 140_000, outfile=f)

    primesObj = PrimesFromFile(f_primes)
    return f_primes, primesObj


def test_PrimesFromFile_obj(primes_file_obj):
    # Create primes.txt if it doesn't exist
    f_primes, primes_obj = primes_file_obj
    assert primes_obj.max == 139_999
    assert len(primes_obj.primes) == 13_010

    # Cleanup
    if os.path.exists(f_primes):
        os.remove(f_primes)


def test_parse_factor_line():
    # parse_factor_line doesn't check for correctness
    assert parse_factor_line("6: 2 3") == (6, (2, 3))
    assert parse_factor_line("6: \t2 \t3") == (6, (2, 3))
    assert parse_factor_line("6: 3 2") == (6, (3, 2))  # order matters
    assert parse_factor_line("36: 2 2 3 3") == (36, (2, 2, 3, 3))

    with pytest.raises(ValueError):
        parse_factor_line("6 3 2")
        parse_factor_line("6.1: 3 2")
