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


@pytest.mark.xdist_group(name="arg_group")
def test_healg_arg_header(hekit_path):
    """Verify that gen-primes cmd is excuted correctly
    when p and d are single numbers"""
    cmd = f"{hekit_path} algebras -p 2 -d 3"
    act_result = execute_process(cmd)
    assert (
        "2                    3                    7                    6                    2"
        in act_result.stdout
    )
    assert (
        "p                    d                    m                   phim                nslots"
        in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_healg_arg_no_header(hekit_path):
    """Verify that algebras cmd is excuted correctly when
    --no-header flag is used"""
    cmd = f"{hekit_path} algebras -p 2 -d 3 --no-header"
    act_result = execute_process(cmd)
    assert (
        "2                    3                    7                    6                    2"
        in act_result.stdout
    )
    assert (
        "p                    d                    m                   phim                nslots"
        not in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_healg_arg_p(hekit_path):
    """Verify that gen-primes cmd is excuted correctly when
    p is a list of numbers"""
    cmd = f"{hekit_path} algebras -p 7,13 -d 1 --no-header"
    act_result = execute_process(cmd)
    assert (
        "7                    1                    2                    1                    1"
        in act_result.stdout
    )
    assert (
        "13                   1                    12                   4                    4"
        in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_healg_negative_arg_p(hekit_path):
    """Verify that gen-primes cmd triggers an error when
    p is a negative number"""
    cmd = f"{hekit_path} algebras -p -7 -d 1 --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -p: Wrong syntax for range given '-7'"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_healg_max_arg_p(hekit_path):
    """Verify that gen-primes cmd is excuted correctly when
    p is equal to sys.maxsize"""
    cmd = f"{hekit_path} algebras -p {sys.maxsize} -d 7 --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -p: invalid parse_range_for_primes value"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_healg_arg_d(hekit_path):
    """Verify that gen-primes cmd is excuted correctly when
    d is a list of numbers"""
    cmd = f"{hekit_path} algebras -p 2 -d 3,5 --no-header"
    act_result = execute_process(cmd)
    assert (
        "2                    3                    7                    6                    2"
        in act_result.stdout
    )
    assert (
        "2                    5                    31                   30                   6"
        in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_healg_negative_arg_d(hekit_path):
    """Verify that gen-primes cmd triggers an error when
    d is a negative number"""
    cmd = f"{hekit_path} algebras -p 7 -d -1 --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -d: Wrong syntax for range given '-1'"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.skip(reason="Not realistic test because SW cannot handle that amount in d")
def test_healg_max_arg_d(hekit_path):
    """Verify that gen-primes cmd is excuted correctly when
    d is equal to sys.maxsize"""
    cmd = f"{hekit_path} -p 7 -d {sys.maxsize} --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -d: invalid parse_range_for_primes value"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_healg_arg_no_corrected(hekit_path):
    """Verify that algebras cmd is excuted correctly when
    --no-corrected flag is used"""
    cmd = f"{hekit_path} algebras -p 11,19,23 -d 2,4,5 --no-header --no-corrected "
    act_result = execute_process(cmd)
    assert (
        "11                   2                    3                    2                    1"
        in act_result.stdout
    )
    assert (
        "23                   5                 6436342              2925600               585120"
        in act_result.stdout
    )
    assert not act_result.stderr
    assert 0 == act_result.returncode
