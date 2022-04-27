# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from .context import healg
from healg import parse_cmdline, main 


def test_main_arg_header(mocker):
    """Arrange"""
    cmdline_args = ""
    width = 20
    exp_output = f"{'p' :^{width}} {'d' :^{width}} {'m' :^{width}} {'phim' :^{width}} {'nslots' :^{width}}"
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")

    """Act"""
    args = parse_cmdline(cmdline_args)

    """Assert"""
    assert main(args) is None
    assert 2 == mock_print.call_count
    mock_print.assert_called_with(exp_output)

def test_main_arg_no_header(mocker):
    """Arrange"""
    cmdline_args = "--no-header".split()
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")

    """Act"""
    args = parse_cmdline(cmdline_args)

    """Assert"""
    assert main(args) is None
    mock_print.assert_not_called()


def test_main_arg_p(mocker):
    """Arrange"""
    cmdline_args = "-p 7 --no-header".split()
    width = 20
    exp_output = f"{'7' :^{width}} {'1' :^{width}} {'6' :^{width}} {'2' :^{width}} {'2' :^{width}}"
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")

    """Act"""
    args = parse_cmdline(cmdline_args)

    """Assert"""
    assert main(args) is None
    assert 3 == mock_print.call_count
    mock_print.assert_called_with(exp_output)

def test_main_arg_d(mocker):
    """Arrange"""
    cmdline_args = "-p 2 -d 4-5 --no-header".split()
    width = 20
    exp_output = f"{'2' :^{width}} {'5' :^{width}} {'31' :^{width}} {'30' :^{width}} {'6' :^{width}}"   
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")

    """Act"""
    args = parse_cmdline(cmdline_args)

    """Assert"""
    assert main(args) is None
    assert 4 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_main_arg_no_corrected(mocker):
    """Arrange"""
    cmdline_args = "-p 11-25 -d 2,4-5 --no-corrected --no-header".split()
    width = 20
    exp_output = f"{'25' :^{width}} {'5' :^{width}} {'9765624' :^{width}} {'2912000' :^{width}} {'582400' :^{width}}"   
    mock_PrimesFromFile = mocker.patch("healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("healg.print")

    """Act"""
    args = parse_cmdline(cmdline_args)

    """Assert"""
    assert main(args) is None
    assert 786 == mock_print.call_count
    mock_print.assert_called_with(exp_output)

