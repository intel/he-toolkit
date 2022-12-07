# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import sys
from tests.common_utils import execute_process, hekit_path


@pytest.mark.xdist_group(name="arg_group")
def test_arg_header(hekit_path):
    """Verify that the algebras cmd is executed correctly
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
def test_arg_no_header(hekit_path):
    """Verify that the algebras cmd is executed correctly when
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
def test_arg_p(hekit_path):
    """Verify that the algebras cmd is executed correctly when
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
def test_negative_arg_p(hekit_path):
    """Verify that the algebras cmd triggers an error when
    p is a negative number"""
    cmd = f"{hekit_path} algebras -p -7 -d 1 --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -p: Wrong syntax for range given '-7'"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_max_arg_p(hekit_path):
    """Verify that the algebras cmd is executed correctly when
    p is equal to sys.maxsize"""
    cmd = f"{hekit_path} algebras -p {sys.maxsize} -d 7 --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -p: invalid parse_range_for_primes value"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_arg_d(hekit_path):
    """Verify that the algebras cmd is executed correctly when
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
def test_negative_arg_d(hekit_path):
    """Verify that the algebras cmd triggers an error when
    d is a negative number"""
    cmd = f"{hekit_path} algebras -p 7 -d -1 --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -d: Wrong syntax for range given '-1'"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.skip(reason="Not realistic test because SW cannot handle that amount in d")
def test_max_arg_d(hekit_path):
    """Verify that the algebras cmd is executed correctly when
    d is equal to sys.maxsize"""
    cmd = f"{hekit_path} algebras -p 7 -d {sys.maxsize} --no-header"
    act_result = execute_process(cmd)
    assert (
        "hekit algebras: error: argument -d: invalid parse_range_for_primes value"
        in act_result.stderr
    )
    assert 0 != act_result.returncode


@pytest.mark.xdist_group(name="arg_group")
def test_arg_no_corrected(hekit_path):
    """Verify that algebras cmd is executed correctly when
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
