# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest

from .context import hekit, command_check_deps
from hekit import main
from command_check_deps import check_dependencies


def test_check_dependencies_not_found(mocker):
    """Arrange"""
    args = MockArgs()

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    # Mocking objects from command_check_deps
    mock_print = mocker.patch("command_check_deps.print")
    mock_which = mocker.patch("command_check_deps.which")
    mock_which.side_effect = [False, False, False]

    """Act"""
    main()

    """Assert"""
    mock_print.assert_any_call(
        "'programA' was not found, a minimum 'programA 3.8' is required"
    )
    mock_print.assert_any_call("'programB' was not found")
    mock_print.assert_any_call(
        "'programC' was not found, an exact 'programC 0.1' is required"
    )


def test_check_dependencies_found(mocker):
    """Arrange"""
    args = MockArgs()

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    # Mocking objects from command_check_deps
    mock_print = mocker.patch("command_check_deps.print")
    mock_which = mocker.patch("command_check_deps.which")
    mock_which.side_effect = [True, True, True]
    mock_run = mocker.patch("command_check_deps.subprocess_run")
    subp_1 = MockSubprocess("programA", 3.8)
    subp_2 = MockSubprocess("programC", 0.1)
    mock_run.side_effect = [subp_1, subp_2]

    """Act"""
    main()

    """Assert"""
    mock_print.assert_any_call(f"'{subp_1.prog} {subp_1.vers}' found")
    mock_print.assert_any_call("'programB' found")
    mock_print.assert_any_call(f"'{subp_2.prog} {subp_2.vers}' found")


def test_check_dependencies_found_wrong_version(mocker):
    """Arrange"""
    args = MockArgs()

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    # Mocking objects from command_check_deps
    mock_print = mocker.patch("command_check_deps.print")
    mock_which = mocker.patch("command_check_deps.which")
    mock_which.side_effect = [True, False, True]
    mock_run = mocker.patch("command_check_deps.subprocess_run")
    subp_1 = MockSubprocess("programA", 3.5)
    subp_2 = MockSubprocess("programC", 0.5)
    mock_run.side_effect = [subp_1, subp_2]

    """Act"""
    main()

    """Assert"""
    mock_print.assert_any_call(
        f"'{subp_1.prog} {subp_1.vers}' found, but minimum version '3.8' is required"
    )
    mock_print.assert_any_call("'programB' was not found")
    mock_print.assert_any_call(
        f"'{subp_2.prog} {subp_2.vers}' found, but exact version '0.1' is required"
    )


def test_check_dependencies_FileNotFoundError(mocker):
    """Arrange"""
    args = MockArgs()
    args.dependencies_file = "tests/config/no_a_file.txt"

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""

    """Act"""
    with pytest.raises(SystemExit) as exc_info:
        main()

    """Assert"""
    assert exc_info.value.code == 1


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self):
        self.dependencies_file = "tests/config/dependencies.txt"
        self.config = "tests/config/default.config"
        self.fn = check_dependencies
        self.version = False


class MockSubprocess:
    def __init__(self, program, version):
        self.prog = program
        self.vers = version
        self.returncode = 0
        self.message = (
            f"{program} (OS) {version}\nCopyright (C) 2022 \nThis is free software"
        )
        self.stdout = self.message.encode("ascii")
