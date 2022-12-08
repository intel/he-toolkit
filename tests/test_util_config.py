# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from kit.utils.config import Config, config_required, load_config


def test_config_required_without_error(args):
    @config_required
    def to_be_decorated(args):
        assert "/tests/input_files/default.config" in args.config.config_filename
        assert "/.hekit_test/components" in args.config.repo_location

    to_be_decorated(args)


def test_config_required_file_error(args):
    args.config = ""

    @config_required
    def to_be_decorated(args):
        pass

    with pytest.raises(Exception) as exc_info:
        to_be_decorated(args)

    assert "Error while parsing config file" in str(exc_info.value)


def test_config_required_value_error(args):
    args.config = f"{args.tests_path}/input_files/default_wrong.config"

    @config_required
    def to_be_decorated(args):
        pass

    with pytest.raises(Exception) as exc_info:
        to_be_decorated(args)

    assert "Error while parsing config file" in str(exc_info.value)


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.config = f"{self.tests_path}/input_files/default.config"


@pytest.fixture
def args():
    return MockArgs()
