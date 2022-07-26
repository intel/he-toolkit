# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from tests.common_utils import create_config_file, execute_process, get_tests_path


def test_gen_primes_start_less_than_stop():
    """Verify that gen-primes cmd is executed correctly when
    start is less than stop"""
    # Arrange
    cmd = "./hekit gen-primes 0 10"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert "2\n3\n5\n7\n" in out
    assert not err


def test_gen_primes_start_equal_to_stop():
    """Verify that gen-primes cmd is excuted correctly when
    start is equal to stop"""
    # Arrange
    cmd = "./hekit gen-primes 10 10"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert "\n" in out
    assert not err


def test_gen_primes_start_greater_than_stop():
    """Verify that gen-primes cmd triggers an error when
    start is greater than stop"""
    # Arrange
    cmd = "./hekit gen-primes 100 10"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "Error while running subcommand" in err
    assert "TypeError(\"'NoneType' object is not iterable\")" in err


def test_gen_primes_negative_start():
    """Verify that gen-primes cmd triggers an error when
    start is negative"""
    # Arrange
    cmd = "./hekit gen-primes -1 10"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "Error while running subcommand" in err
    assert (
        "ValueError('A negative number was found in the input: [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]')"
        in err
    )


def test_gen_primes_negative_stop():
    """Verify that gen-primes cmd triggers an error when
    start and stop are negative"""
    # Arrange
    cmd = "./hekit gen-primes -5 -1"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "Error while running subcommand" in err
    assert (
        "ValueError('A negative number was found in the input: [-5, -4, -3, -2, -1]')"
        in err
    )


def test_gen_primes_max_stop():
    """Verify that gen-primes cmd triggers an error when
    stop is equal to sys.maxsize"""
    # Arrange
    cmd = f"./hekit gen-primes -5 {sys.maxsize}"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert "Error while running subcommand" in err
    assert "OverflowError('Python int too large to convert to C ssize_t')" in err


def test_healg_arg_header():
    """Verify that gen-primes cmd is excuted correctly
    when p and d are single numbers"""
    # Arrange
    cmd = "./hekit algebras -p 2 -d 3"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert (
        "2                    3                    7                    6                    2"
        in out
    )
    assert (
        "p                    d                    m                   phim                nslots"
        in out
    )
    assert not err


def test_healg_arg_no_header():
    """Verify that algebras cmd is excuted correctly when
    --no-header flag is used"""
    # Arrange
    cmd = "./hekit algebras -p 2 -d 3 --no-header"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert (
        "2                    3                    7                    6                    2"
        in out
    )
    assert (
        "p                    d                    m                   phim                nslots"
        not in out
    )
    assert not err


def test_healg_arg_p():
    """Verify that gen-primes cmd is excuted correctly when
    p is a list of numbers"""
    # Arrange
    cmd = "./hekit algebras -p 7,13 -d 1 --no-header"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert (
        "7                    1                    2                    1                    1"
        in out
    )
    assert (
        "13                   1                    12                   4                    4"
        in out
    )
    assert not err


def test_healg_negative_arg_p():
    """Verify that gen-primes cmd triggers an error when
    p is a negative number"""
    # Arrange
    cmd = "./hekit algebras -p -7 -d 1 --no-header"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert (
        "hekit algebras: error: argument -p: Wrong syntax for range given '-7'" in err
    )


def test_healg_max_arg_p():
    """Verify that gen-primes cmd is excuted correctly when
    p is equal to sys.maxsize"""
    # Arrange
    cmd = f"./hekit algebras -p {sys.maxsize} -d 7 --no-header"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert (
        "hekit algebras: error: argument -p: invalid parse_range_for_primes value"
        in err
    )


def test_healg_arg_d():
    """Verify that gen-primes cmd is excuted correctly when
    d is a list of numbers"""
    # Arrange
    cmd = "./hekit algebras -p 2 -d 3,5 --no-header"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert (
        "2                    3                    7                    6                    2"
        in out
    )
    assert (
        "2                    5                    31                   30                   6"
        in out
    )
    assert not err


def test_healg_negative_arg_d():
    """Verify that gen-primes cmd triggers an error when
    d is a negative number"""
    # Arrange
    cmd = "./hekit algebras -p 7 -d -1 --no-header"

    # Act
    _, err = execute_process(cmd)

    # Assert
    assert (
        "hekit algebras: error: argument -d: Wrong syntax for range given '-1'" in err
    )


@pytest.mark.skip(reason="Not realistic test because SW cannot handle that amount in d")
def test_healg_max_arg_d(mocker):
    """Verify that gen-primes cmd is excuted correctly when
    d is equal to sys.maxsize"""
    # Arrange
    cmd = f"./hekit algebras -p 7 -d {sys.maxsize} --no-header"

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert (
        "hekit algebras: error: argument -d: invalid parse_range_for_primes value"
        in err
    )


def test_healg_arg_no_corrected():
    """Verify that algebras cmd is excuted correctly when
    --no-corrected flag is used"""
    # Arrange
    cmd = "./hekit algebras -p 11,13,17,19,23 -d 2,4,5 --no-header --no-corrected "

    # Act
    out, err = execute_process(cmd)

    # Assert
    assert (
        "11                   2                    3                    2                    1"
        in out
    )
    assert (
        "23                   5                 6436342              2925600               585120"
        in out
    )
    assert not err
