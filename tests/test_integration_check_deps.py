# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path

from kit.hekit import main
from kit.commands.check_deps import check_dependencies


def test_check_dependencies_not_found(mocker):
    args = MockArgs()
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""
    mockers.mock_which.side_effect = [False, False, False]

    main()
    mockers.mock_print.assert_any_call(
        "'programA' was not found, a minimum 'programA 3.8' is required"
    )
    mockers.mock_print.assert_any_call("'programB' was not found")
    mockers.mock_print.assert_any_call(
        "'programC' was not found, an exact 'programC 0.1' is required"
    )


def test_check_dependencies_found(mocker):
    args = MockArgs()
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""
    mockers.mock_which.side_effect = [True, True, True]
    subp_1 = MockSubprocess("programA", 3.8)
    subp_2 = MockSubprocess("programC", 0.1)
    mockers.mock_run.side_effect = [subp_1, subp_2]

    main()
    mockers.mock_print.assert_any_call(f"'{subp_1.prog} {subp_1.vers}' found")
    mockers.mock_print.assert_any_call("'programB' found")
    mockers.mock_print.assert_any_call(f"'{subp_2.prog} {subp_2.vers}' found")


def test_check_dependencies_found_wrong_version(mocker):
    args = MockArgs()
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""
    mockers.mock_which.side_effect = [True, False, True]
    subp_1 = MockSubprocess("programA", 3.5)
    subp_2 = MockSubprocess("programC", 0.5)
    mockers.mock_run.side_effect = [subp_1, subp_2]

    main()
    mockers.mock_print.assert_any_call(
        f"'{subp_1.prog} {subp_1.vers}' found, but minimum version '3.8' is required"
    )
    mockers.mock_print.assert_any_call("'programB' was not found")
    mockers.mock_print.assert_any_call(
        f"'{subp_2.prog} {subp_2.vers}' found, but exact version '0.1' is required"
    )


def test_check_dependencies_FileNotFoundError(mocker):
    args = MockArgs()
    args.dependencies_file = "/tests/input_files/no_a_file.txt"
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


"""Utilities used by the tests"""


class Mockers:
    def __init__(self, mocker):
        self.mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
        self.mock_print = mocker.patch("kit.commands.check_deps.print")
        self.mock_which = mocker.patch("kit.commands.check_deps.which")
        self.mock_run = mocker.patch("kit.commands.check_deps.subprocess_run")


class MockArgs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.dependencies_file = f"{self.tests_path}/input_files/dependencies.txt"
        self.config = f"{self.tests_path}/input_files/default.config"
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
