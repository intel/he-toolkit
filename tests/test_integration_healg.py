# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import sys
from sys import stderr
from pathlib import Path
from kit.hekit import main
from kit.tools.healg import healg, gen_primes


def test_gen_primes_start_less_than_stop(mocker):
    """Arrange"""
    args = MockArgsGenPrimes()
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 1 == mock_print.call_count


def test_gen_primes_start_equal_to_stop(mocker):
    """Arrange"""
    args = MockArgsGenPrimes()
    args.stop = args.start
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 1 == mock_print.call_count


def test_gen_primes_start_greater_than_stop(mocker):
    """Arrange"""
    args = MockArgsGenPrimes()
    args.stop = 10
    args.start = 100
    mock_exit = mocker.patch("kit.hekit.sys_exit")
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print_main = mocker.patch("kit.hekit.print")

    """Act"""
    main()

    """Assert"""
    mock_exit.assert_called_once_with(1)
    mock_print.assert_not_called()
    mock_exit.assert_called_once_with(1)
    mock_print_main.assert_called_with(
        "Error while running subcommand\n",
        "TypeError(\"'NoneType' object is not iterable\")",
        file=stderr,
    )


def test_gen_primes_negative_start(mocker):
    """Arrange"""
    args = MockArgsGenPrimes()
    args.start = -1
    mock_exit = mocker.patch("kit.hekit.sys_exit")
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print_main = mocker.patch("kit.hekit.print")

    """Act"""
    main()

    """Assert"""
    mock_print.assert_not_called()
    mock_exit.assert_called_once_with(1)
    mock_print_main.assert_called_with(
        "Error while running subcommand\n",
        "ValueError('A negative number was found in the input: [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]')",
        file=stderr,
    )


def test_gen_primes_negative_stop(mocker):
    """Arrange"""
    args = MockArgsGenPrimes()
    args.start = -5
    args.stop = -1
    mock_exit = mocker.patch("kit.hekit.sys_exit")
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print_main = mocker.patch("kit.hekit.print")

    """Act"""
    main()

    """Assert"""
    mock_exit.assert_called_once_with(1)
    mock_print.assert_not_called()
    mock_print_main.assert_called_with(
        "Error while running subcommand\n",
        "ValueError('A negative number was found in the input: [-5, -4, -3, -2, -1]')",
        file=stderr,
    )


def test_gen_primes_max_stop(mocker):
    """Arrange"""
    args = MockArgsGenPrimes()
    args.stop = sys.maxsize
    mock_exit = mocker.patch("kit.hekit.sys_exit")
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print_main = mocker.patch("kit.hekit.print")

    """Act"""
    main()

    """Assert"""
    mock_print.assert_not_called()
    mock_exit.assert_called_once_with(1)
    mock_print_main.assert_called_with(
        "Error while running subcommand\n",
        "OverflowError('Python int too large to convert to C ssize_t')",
        file=stderr,
    )


def test_healg_arg_header(mocker):
    """Arrange"""
    args = MockArgsHealg()
    width = 20
    exp_output = f"{'p' :^{width}} {'d' :^{width}} {'m' :^{width}} {'phim' :^{width}} {'nslots' :^{width}}"
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 2 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_healg_arg_no_header(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_header = False
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    mock_print.assert_not_called()


def test_healg_arg_p(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_header = False
    args.p = [7]
    width = 20
    exp_output = f"{'7' :^{width}} {'1' :^{width}} {'6' :^{width}} {'2' :^{width}} {'2' :^{width}}"
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 3 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_healg_negative_arg_p(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_header = False
    args.p = [-1]
    mock_exit = mocker.patch("kit.hekit.sys_exit")
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print_main = mocker.patch("kit.hekit.print")

    """Act"""
    main()

    """Assert"""
    mock_exit.assert_called_once_with(1)
    mock_print_main.assert_called_with(
        "Error while running subcommand\n",
        "ValueError('A negative number was found in the input: [-2]')",
        file=stderr,
    )


def test_healg_max_arg_p(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_header = False
    args.p = [sys.maxsize]
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    mock_print = mocker.patch("kit.tools.healg.print")

    """Act"""
    main()

    """Assert"""
    assert 15 == mock_print.call_count


def test_healg_arg_d(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_header = False
    args.d = [4, 5]
    args.p = [2]
    width = 20
    exp_output = f"{'2' :^{width}} {'5' :^{width}} {'31' :^{width}} {'30' :^{width}} {'6' :^{width}}"
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 4 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_healg_negative_arg_d(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_header = False
    args.d = [-1]
    args.p = [2]
    width = 20
    mock_exit = mocker.patch("kit.hekit.sys_exit")
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print_main = mocker.patch("kit.hekit.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    mock_exit.assert_called_once_with(1)
    mock_print_main.assert_called_with(
        "Error while running subcommand\n",
        "ValueError('A negative number was found in the input: [-0.5]')",
        file=stderr,
    )


@pytest.mark.skip(reason="check later")
def test_healg_max_arg_d(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_header = False
    args.d = [sys.maxsize]
    args.p = [2]
    width = 20
    exp_output = f"{'2' :^{width}} {'5' :^{width}} {'31' :^{width}} {'30' :^{width}} {'6' :^{width}}"
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 4 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


def test_healg_arg_no_corrected(mocker):
    """Arrange"""
    args = MockArgsHealg()
    args.no_corrected = False
    args.no_header = False
    args.d = [2, 4, 5]
    args.p = [11, 13, 17, 19, 23]
    width = 20
    exp_output = f"{'23' :^{width}} {'5' :^{width}} {'6436342' :^{width}} {'2925600' :^{width}} {'585120' :^{width}}"
    mock_PrimesFromFile = mocker.patch("kit.tools.healg.PrimesFromFile")
    mock_PrimesFromFile.is_prime.return_value = True
    mock_print = mocker.patch("kit.tools.healg.print")
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    main()

    """Assert"""
    assert 376 == mock_print.call_count
    mock_print.assert_called_with(exp_output)


class MockArgsHealg:
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


class MockArgsGenPrimes:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.version = False
        self.stop = 10
        self.start = 0
        self.fn = gen_primes
        self.config = f"{self.tests_path}/input_files/default.config"
        self.tests_path = Path(__file__).resolve().parent
