# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import os
from pathlib import Path
from subprocess import run
from typing import List, Tuple


def test_default(CONFIG_PSI_DIR):
    """Test ./datagen column-description with no options"""
    # Run datagen
    result = run(
        [
            CONFIG_PSI_DIR + "/scripts/datagen.py",
            CONFIG_PSI_DIR + "/scripts/columns.toml",
        ],
        encoding="utf-8",
        capture_output=True,
        check=True,
    )

    # Check result
    assert not result.stderr
    assert 0 == result.returncode
    # Default number of rows is 10 plus the column header row
    assert 11 == result.stdout.count("\n")


def test_total_flag(CONFIG_PSI_DIR):
    """Test the use of the total flag correctly determines number of rows"""
    # Run datagen with 4 rows
    rows = 4
    result = run(
        [
            CONFIG_PSI_DIR + "/scripts/datagen.py",
            CONFIG_PSI_DIR + "/scripts/columns.toml",
            "--total",
            str(rows),
        ],
        encoding="utf-8",
        capture_output=True,
        check=True,
    )

    # Check result
    assert not result.stderr
    assert 0 == result.returncode
    # Default number of rows is 4 plus the column header row
    assert rows + 1 == result.stdout.count("\n")

    # Change total rows to 15
    rows = 15
    result = run(
        [
            CONFIG_PSI_DIR + "/scripts/datagen.py",
            CONFIG_PSI_DIR + "/scripts/columns.toml",
            "--total",
            str(rows),
        ],
        encoding="utf-8",
        capture_output=True,
        check=True,
    )

    # Check result
    assert not result.stderr
    assert 0 == result.returncode
    # Default number of rows is 15 plus the column header row
    assert rows + 1 == result.stdout.count("\n")


def test_real_flag(input_data, CONFIG_PSI_DIR):
    """Test creating new csv from input data"""
    input_size = 5
    result_size = 8
    intersect_size = 3

    # Create the input data
    path, data = input_data

    # Create the new data selecting 3 random rows from input data
    result = run(
        [
            CONFIG_PSI_DIR + "/scripts/datagen.py",
            CONFIG_PSI_DIR + "/scripts/columns.toml",
            str(path),
            "--total",
            str(result_size),
            "--real",
            str(intersect_size),
        ],
        encoding="utf-8",
        capture_output=True,
        check=True,
    )

    # Check result
    assert not result.stderr
    assert 0 == result.returncode
    # Default number of rows is 5 plus the column header row
    assert result_size + 1 == result.stdout.count("\n")

    input_set = set(data)
    result_set = set(result.stdout.rstrip().split("\n"))

    assert len(input_set) == input_size
    assert len(result_set) == result_size + 1
    assert len(input_set & result_set) == intersect_size + 1


def test_throw_when_real_greater_than_total(input_data, CONFIG_PSI_DIR):
    """datagen throws when trying to select more values than total size"""
    result_size = 2
    intersect_size = 3

    # Create the input data
    path, data = input_data

    # Create the new data selecting 3 random rows from input data
    result = run(
        [
            CONFIG_PSI_DIR + "/scripts/datagen.py",
            CONFIG_PSI_DIR + "/scripts/columns.toml",
            str(path),
            "--total",
            str(result_size),
            "--real",
            str(intersect_size),
        ],
        encoding="utf-8",
        capture_output=True,
    )

    # Check result
    assert (
        f"Number of chosen real matches '{intersect_size}' must not exceed total '{result_size}'"
        in result.stderr
    )
    assert 0 != result.returncode


@pytest.fixture
def CONFIG_PSI_DIR() -> str:
    return os.environ["CONFIG_PSI_DIR"]


@pytest.fixture
def input_data(tmp_path, CONFIG_PSI_DIR) -> Tuple[Path, List[str]]:
    """Fixture for creating input data. Returns path to file and raw data"""
    path = tmp_path / "input.csv"
    input_data = run(
        " ".join(
            [
                CONFIG_PSI_DIR + "/scripts/datagen.py",
                CONFIG_PSI_DIR + "/scripts/columns.toml",
                "--total",
                "4",
                ">",
                str(path),
            ]
        ),
        encoding="utf-8",
        capture_output=True,
        check=True,
        shell=True,
    )

    with path.open() as f:
        lines = f.readlines()
    lines = [line.rstrip() for line in lines]

    return path, lines
