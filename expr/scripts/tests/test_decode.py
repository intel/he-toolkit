# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from types import SimpleNamespace
from typing import Callable
import pytest

from config import Config
from ptxt import Params
from decode import *


def test_sum_vectors():
    vectors = [[1, 2, 3], [2, 1, 0], [6, 6, 6]]
    assert sum_vectors(*vectors) == [9, 9, 9]


def test_sum_segments():
    no_segs = 4
    upto_10 = list([i] for i in range(10))
    nums = []
    for i in range(no_segs):
        nums.extend(upto_10 if i % 2 else reversed(upto_10))
    print(nums)
    for total in sum_segments(nums, no_segs):
        assert total == [18]


def test_parse_header_with_two_numbers():
    header_str = "2 3"
    assert (2, 3) == parse_header(header_str)


def test_parse_header_with_one_number():
    header_str = "3"
    assert (3, 1) == parse_header(header_str)


def test_parse_args(example_config_and_data_files):
    configfilepath, datafilepath, _ = example_config_and_data_files(
        "test.config", "test.data"
    )
    cmdline_args = f"--config {configfilepath} {datafilepath}".split()
    args = parse_args(cmdline_args)
    expected_obj = {
        "datafile": str(datafilepath),
        "config": Config(
            params=Params(m=45, p=19),
            encodings=None,
            composites=None,
            segments=1,
            columns=1,
        ),
        "entries": 0,
    }
    assert vars(args) == expected_obj


def test_invalid_entries_arg(example_config_and_data_files):
    configfilepath, datafilepath, _ = example_config_and_data_files(
        "test.config", "test.data"
    )
    cmdline_args = f"--config {configfilepath} --entries -1 {datafilepath}".split()
    with pytest.raises(SystemExit):
        parse_args(cmdline_args)


def test_main(capfd, empty_obj, example_config_and_data_files):
    args = empty_obj
    args.params, args.datafile, indices = example_config_and_data_files(
        "test.params", "test.data"
    )
    args.config.segments = 1
    args.entries = 0
    main(args)
    captured = capfd.readouterr()
    expected_out = "\n".join([f"Match on line '{i+1}'" for i in indices]) + "\n"
    assert captured.out == expected_out


def test_ignore_padding(capfd, empty_obj, example_config_and_data_files):
    args = empty_obj
    args.params, args.datafile, indices = example_config_and_data_files(
        "test.params", "test.data"
    )
    args.segment = 1
    args.entries = 9  # Only count first 9 lines
    main(args)
    captured = capfd.readouterr()
    expected_out = "\n".join([f"Match on line '{i+1}'" for i in indices]) + "\n"
    assert captured.out == expected_out  # No difference because last match is entry 9

    args.entries = 7  # This should now ignore the match on line 9
    main(args)
    captured = capfd.readouterr()
    # Match on line 9 should be missing from captured.out
    assert captured.out != expected_out
    new_expected_out = (
        "\n".join([f"Match on line '{i+1}'" for i in indices if i <= args.entries])
        + "\n"
    )
    assert captured.out == new_expected_out


@pytest.fixture
def empty_obj():
    """Empty object. Useful for late binding attribs."""
    return SimpleNamespace()


@pytest.fixture
def example_config_and_data_files(tmp_path: Path) -> Callable:
    """Create in a tmp dir an example config and data file."""

    def _create_func(config_filename: str, datafile_filename: str):
        # Create config file
        config_path = tmp_path / config_filename
        config_path.write_text(
            """
        [config]
        segments = 1
        columns = 1
        [params]
        m = 45
        p = 19
        """
        )

        # Create data file
        datafile_path = tmp_path / datafile_filename
        config = Config.from_toml(config_path.resolve(), params_only=True)
        params = config.params
        ptxt = Ptxt(params)
        indices = [2, 5, 8]  # sorted unique nums
        ptxt.insert_data([1] if i in indices else [0] for i in range(params.nslots))
        out = f"1\n{ptxt.to_json()}\n"
        datafile_path.write_text(out)
        return config_path.resolve(), datafile_path.resolve(), indices

    return _create_func
