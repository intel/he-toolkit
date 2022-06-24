# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from kit.commands.check_deps import (
    version_string_to_tuple,
    parse_dependencies,
    check_dependency,
    check_dependencies,
    Op,
)


def test_version_string_to_tuple_several_numbers():
    """Arrange"""
    ver_str = "5.56.45.4568"

    """Act"""
    exp_value = version_string_to_tuple(ver_str)

    """Assert"""
    assert exp_value == (5, 56, 45, 4568)


def test_version_string_to_tuple_one_numbers():
    """Arrange"""
    ver_str = "5"

    """Act"""
    exp_value = version_string_to_tuple(ver_str)

    """Assert"""
    assert exp_value == (5,)


def test_version_string_to_tuple_empty():
    """Arrange"""
    ver_str = ""

    """Act"""
    with pytest.raises(ValueError) as exc_info:
        version_string_to_tuple(ver_str)

    """Assert"""
    assert str(exc_info.value) == f"Invalid version number '{ver_str}'"


def test_version_string_to_tuple_String():
    """Arrange"""
    ver_str = "5.56.45.5s.4568"

    """Act"""
    with pytest.raises(ValueError) as exc_info:
        version_string_to_tuple(ver_str)

    """Assert"""
    assert str(exc_info.value) == f"Invalid version number '{ver_str}'"


def test_parse_dependencies_greater_than(mocker):
    """Arrange"""
    exp_lib = "lib"
    exp_op = ">="
    exp_vers = "1.2.3"
    dep_and_ver_str = f"{exp_lib} {exp_op} {exp_vers}"

    """Act"""
    exp_value = parse_dependencies(dep_and_ver_str)

    """Assert"""
    assert exp_value.name == exp_lib
    assert exp_value.operation == Op.MIN
    assert exp_value.version == (1, 2, 3)
    assert exp_value.ver_str == exp_vers


def test_parse_dependencies_equals_to(mocker):
    """Arrange"""
    exp_lib = "lib"
    exp_op = "=="
    exp_vers = "1.5.3"
    dep_and_ver_str = f"{exp_lib} {exp_op} {exp_vers}"

    """Act"""
    exp_value = parse_dependencies(dep_and_ver_str)

    """Assert"""
    assert exp_value.name == exp_lib
    assert exp_value.operation == Op.EXACT
    assert exp_value.version == (1, 5, 3)
    assert exp_value.ver_str == exp_vers


def test_parse_dependencies_any(mocker):
    """Arrange"""
    exp_lib = "lib"
    dep_and_ver_str = f"{exp_lib}"

    """Act"""
    exp_value = parse_dependencies(dep_and_ver_str)

    """Assert"""
    assert exp_value.name == exp_lib
    assert exp_value.operation == Op.ANY
    assert exp_value.version == ()
    assert exp_value.ver_str == ""


def test_check_dependency_not_found_any(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.ANY
    exp_vers = "1.2.3"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = False

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(f"'{exp_name}' was not found")


def test_check_dependency_not_found_exact(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.EXACT
    exp_vers = "4.5.6"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = False

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(
        f"'{exp_name}' was not found, an exact '{exp_name} {exp_vers}' is required"
    )


def test_check_dependency_not_found_min(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.MIN
    exp_vers = "7.8.9"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = False

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(
        f"'{exp_name}' was not found, a minimum '{exp_name} {exp_vers}' is required"
    )


def test_check_dependency_found_any(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.ANY
    exp_vers = "1.2.3"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = True

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(f"'{exp_name}' found")


def test_check_dependency_found_exact(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.EXACT
    exp_vers = "1.2.3"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = True
    mock_run = mocker.patch("kit.commands.check_deps.subprocess_run")
    mock_run.return_value = MockSubprocess(exp_name, exp_vers)

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(f"'{exp_name} {exp_vers}' found")


def test_check_dependency_found_exact_wrong_version(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.EXACT
    exp_vers = "1.2.3"
    act_vers = "5.6.3"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = True
    mock_run = mocker.patch("kit.commands.check_deps.subprocess_run")
    mock_run.return_value = MockSubprocess(exp_name, act_vers)

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(
        f"'{exp_name} {act_vers}' found, but exact version '{exp_vers}' is required"
    )


def test_check_dependency_found_min(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.MIN
    exp_vers = "1.2.3"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = True
    mock_run = mocker.patch("kit.commands.check_deps.subprocess_run")
    mock_run.return_value = MockSubprocess(exp_name, exp_vers)

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(f"'{exp_name} {exp_vers}' found")


def test_check_dependency_found_min_wrong_version(mocker):
    """Arrange"""
    exp_name = "lib"
    exp_op = Op.MIN
    exp_vers = "7.2.3"
    act_vers = "5.6.3"
    dep = MockDep(exp_name, exp_op, exp_vers)
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_which = mocker.patch("kit.commands.check_deps.which")
    mock_which.return_value = True
    mock_run = mocker.patch("kit.commands.check_deps.subprocess_run")
    mock_run.return_value = MockSubprocess(exp_name, act_vers)

    """Act"""
    check_dependency(dep)

    """Assert"""
    mock_print.assert_called_with(
        f"'{exp_name} {act_vers}' found, but minimum version '{exp_vers}' is required"
    )


def test_check_dependencies(mocker):
    """Arrange"""
    args = MockArgs()

    mock_check = mocker.patch("kit.commands.check_deps.check_dependencies_list")
    mock_open = mocker.patch.object(Path, "open")
    mock_readlines = mock_open.return_value
    mock_readlines.readlines.return_value = "lib >= 1.2.3"

    """Act"""
    check_dependencies(args)

    """Assert"""
    mock_check.assert_called_once()


def test_check_dependencies_FileNotFoundError(mocker):
    """Arrange"""
    args = MockArgs()

    mock_check = mocker.patch("kit.commands.check_deps.check_dependencies_list")
    mock_print = mocker.patch("kit.commands.check_deps.print")
    mock_open = mocker.patch.object(Path, "open")
    mock_open.side_effect = FileNotFoundError()

    """Act"""
    with pytest.raises(SystemExit) as exc_info:
        check_dependencies(args)

    """Assert"""
    assert exc_info.value.code == 1
    mock_print.assert_called_with("File '/home' does not exist")
    mock_check.assert_not_called()


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self):
        self.dependencies_file = "/home"


class MockDep:
    def __init__(self, name, operation, ver_str):
        self.name = name
        self.operation = operation
        self.ver_str = ver_str
        self.version = version_string_to_tuple(ver_str)


class MockSubprocess:
    def __init__(self, program, version):
        self.prog = program
        self.vers = version
        self.returncode = 0
        self.message = (
            f"{program} (OS) {version}\nCopyright (C) 2022 \nThis is free software"
        )
        self.stdout = self.message.encode("ascii")
