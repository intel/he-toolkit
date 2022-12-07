# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import sys
from tests.common_utils import execute_process, hekit_path


def test_gen_primes_start_less_than_stop(hekit_path):
    """Verify that gen-primes cmd is executed correctly when
    start is less than stop"""
    cmd = f"{hekit_path} gen-primes 0 10"
    act_result = execute_process(cmd)
    assert "2\n3\n5\n7\n" in act_result.stdout
    assert not act_result.stderr
    assert 0 == act_result.returncode


def test_gen_primes_start_equal_to_stop(hekit_path):
    """Verify that gen-primes cmd is executed correctly when
    start is equal to stop"""
    cmd = f"{hekit_path} gen-primes 10 10"
    act_result = execute_process(cmd)
    assert "\n" in act_result.stdout
    assert not act_result.stderr
    assert 0 == act_result.returncode


def test_gen_primes_start_greater_than_stop(hekit_path):
    """Verify that gen-primes cmd triggers an error when
    start is greater than stop"""
    cmd = f"{hekit_path} gen-primes 100 10"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert (
        "ValueError(\"start '100' should not be larger than stop '10'\")"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


def test_gen_primes_negative_start(hekit_path):
    """Verify that gen-primes cmd triggers an error when
    start is negative"""
    cmd = f"{hekit_path} gen-primes -1 10"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert (
        "ValueError('A negative number was found in the input: [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]')"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


def test_gen_primes_negative_stop(hekit_path):
    """Verify that gen-primes cmd triggers an error when
    start and stop are negative"""
    cmd = f"{hekit_path} gen-primes -5 -1"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert (
        "ValueError('A negative number was found in the input: [-5, -4, -3, -2, -1]')"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


def test_gen_primes_max_stop(hekit_path):
    """Verify that gen-primes cmd triggers an error when
    stop is equal to sys.maxsize"""
    cmd = f"{hekit_path} gen-primes -5 {sys.maxsize}"
    act_result = execute_process(cmd)
    assert "Error while running subcommand" in act_result.stderr
    assert (
        "OverflowError('Python int too large to convert to C ssize_t')"
        in act_result.stderr
    )
    assert 0 != act_result.returncode
