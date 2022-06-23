# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
import tests.context
from hekit import main
from healg import healg


def test_main_arg_header(mocker):
    """Arrange"""
    args = MockArgs()
    width = 20
    exp_output = f"{'p' :^{width}} {'d' :^{width}} {'m' :^{width}} {'phim' :^{width}} {'nslots' :^{width}}"
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 2 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_main_arg_no_header(mocker):
    """Arrange"""
    args = MockArgs()
    args.no_header = False
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    mock_print.assert_not_called()


def test_main_arg_p(mocker):
    """Arrange"""
    args = MockArgs()
    args.no_header = False
    args.p = [7]
    width = 20
    exp_output = f"{'7' :^{width}} {'1' :^{width}} {'6' :^{width}} {'2' :^{width}} {'2' :^{width}}"
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 3 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_main_arg_d(mocker):
    """Arrange"""
    args = MockArgs()
    args.no_header = False
    args.d = [4, 5]
    args.p = [2]
    width = 20
    exp_output = f"{'2' :^{width}} {'5' :^{width}} {'31' :^{width}} {'30' :^{width}} {'6' :^{width}}"
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 4 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_main_arg_no_corrected(mocker):
    """Arrange"""
    args = MockArgs()
    args.no_corrected = False
    args.no_header = False
    args.d = [2, 4, 5]
    args.p = [11, 13, 17, 19, 23]
    width = 20
    exp_output = f"{'23' :^{width}} {'5' :^{width}} {'6436342' :^{width}} {'2925600' :^{width}} {'585120' :^{width}}"
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 376 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


class MockArgs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.p = [2]
        self.d = [1]
        self.no_corrected = True
        self.no_header = True
        self.version = False
        self.fn = healg
        self.config = f"{self.tests_path}/input_files/default.config"
        self.tests_path = Path(__file__).resolve().parent
