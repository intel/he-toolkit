# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module checks the dependencies that are specified in an input file"""

from __future__ import annotations

from subprocess import CalledProcessError, run as subprocess_run  # nosec B404
from re import search
from shutil import which
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from sys import exit as sys_exit
from kit.utils.subparsers import validate_input


class Op(Enum):
    """Define the operations to compare the dependency’s versions"""

    EXACT = auto()
    MIN = auto()
    ANY = auto()


@dataclass(frozen=True)
class Dep:
    """Define the properties of a dependency"""

    name: str
    operation: Op
    version: tuple[int, ...]
    ver_str: str

    @classmethod
    def make_from_triple(cls, dep_str: str, op_str: str, ver_str: str) -> Dep:
        """Factory that transforms from strings"""
        if op_str == "==":
            op = Op.EXACT
        elif op_str == ">=":
            op = Op.MIN
        else:
            raise ValueError(f"Unrecognized version operator '{op_str}'")

        ver = version_string_to_tuple(ver_str)
        return cls(dep_str, op, ver, ver_str)

    @classmethod
    def make_from_str(cls, dep_str: str) -> Dep:
        """Factory that transforms from string"""
        return cls(dep_str, Op.ANY, tuple(), "")


def version_string_to_tuple(ver_str: str) -> tuple[int, ...]:
    """version '10.11.12' -> (10, 11, 12)"""
    try:
        return tuple(int(i) for i in ver_str.split("."))
    except ValueError as e:
        raise ValueError(f"Invalid version number '{ver_str}'") from e


def parse_dependencies(dep_and_ver_str: str) -> Dep:
    """Separate dependencies, versions, and operations.
    Matches either a string i.e 'python' or triple string i.e. 'python >= 3.8'
    """
    match = search(r"(.*)(>=|==)(.*)", dep_and_ver_str)
    if match:
        dep_str, op_str, ver_str = match.groups()
        return Dep.make_from_triple(dep_str.strip(), op_str, ver_str.strip())

    # else assume str
    return Dep.make_from_str(dep_and_ver_str.strip())


def check_dependency(dep: Dep) -> None:
    """Check the dependency and print what was found."""
    if not which(dep.name):
        msg = f"'{dep.name}' was not found"
        if dep.operation == Op.ANY:
            pass
        elif dep.operation == Op.EXACT:
            msg += f", an exact '{dep.name} {dep.ver_str}' is required"
        elif dep.operation == Op.MIN:
            msg += f", a minimum '{dep.name} {dep.ver_str}' is required"
        else:
            raise ValueError("Unknown operation '{dep.operation}'")
        print(msg)
        return
    # Now deal with when found
    if dep.operation == Op.ANY:
        print(f"'{dep.name}' found")
        return
    version_flag = "--version"

    try:
        output = subprocess_run(  # nosec B603
            [dep.name, version_flag], capture_output=True, check=True
        )
        stdout = output.stdout.decode("utf-8")
        version_found = search(r"\d+(\.\d+)*", stdout)
        if version_found:
            ver_str = version_found.group(0)
            version = version_string_to_tuple(ver_str)
            msg = f"'{dep.name} {ver_str}' found"
            if dep.operation == Op.EXACT and dep.version != version:
                msg += f", but exact version '{dep.ver_str}' is required"
            elif dep.operation == Op.MIN and dep.version > version:
                msg += f", but minimum version '{dep.ver_str}' is required"
            print(msg)
    except CalledProcessError:
        pass


def check_dependencies_list(deps: Iterable[str]) -> None:
    """Check list of dependencies and prints out if found"""
    for dep in map(parse_dependencies, deps):
        check_dependency(dep)


def check_dependencies(args) -> None:
    """Check dependencies described in an input file"""
    path = Path(args.dependencies_file)
    try:
        with path.open(encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File '{path}' does not exist")
        sys_exit(1)

    # filter out comment lines and empty lines
    filtered_lines = (line for line in lines if not search(r"^\s*#|^\s*$", line))

    # At the mo, dependencies file is very constrained
    check_dependencies_list(filtered_lines)


def set_check_dep_subparser(subparsers):
    """create the parser for the 'check-dependencies' command"""
    parser_check_dependencies = subparsers.add_parser(
        "check-dependencies", description="checks system dependencies"
    )
    parser_check_dependencies.add_argument(
        "dependencies_file",
        metavar="dependencies-file",
        type=validate_input,
        help="dependencies file",
    )
    parser_check_dependencies.set_defaults(fn=check_dependencies)
