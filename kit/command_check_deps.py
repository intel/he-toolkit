# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import subprocess
from re import search
from shutil import which
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


class Op(Enum):
    EXACT = auto()
    MIN = auto()
    ANY = auto()


@dataclass(frozen=True)
class Dep:
    name: str
    operation: Op
    version: Tuple[int]
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
        return cls(dep_str, Op.ANY, tuple(), "")


def version_string_to_tuple(ver_str: str) -> Tuple[int]:
    """version '10.11.12' -> (10, 11, 12) """
    try:
        return tuple(int(i) for i in ver_str.split("."))
    except ValueError:
        raise ValueError(f"Invalid version number '{ver_str}'")


def parse_dependencies(dep_and_ver_str: str) -> Dep:
    """Separate dependencies, versions, and operations.
    Matches either a string i.e 'python' or triple string i.e. 'python >= 3.8'
    """
    match = search("(.*)(>=|==)(.*)", dep_and_ver_str)
    if match:
        dep_str, op_str, ver_str = match.groups()
        return Dep.make_from_triple(dep_str.strip(), op_str, ver_str.strip())
    else:  # assume str
        return Dep.make_from_str(dep_and_ver_str.strip())


def check_dependency(dep: Dep) -> None:
    """Check the dependency and print what was found."""
    if not which(dep.name):
        if dep.operation == Op.ANY:
            print(f"'{dep.name}' was not found")
        elif dep.operation == Op.EXACT:
            print(
                f"'{dep.name}' was not found, an exact '{dep.name} {dep.ver_str}' is required"
            )
        elif dep.operation == Op.MIN:
            print(
                f"'{dep.name}' was not found, a minimum '{dep.name} {dep.ver_str}' is required"
            )
        else:
            raise ValueError("Unknown operation '{dep.operation}'")
        return
    # Now deal with when found
    if dep.operation == Op.ANY:
        print(f"'{dep.name}' found")
        return
    version_flag = "--version"
    output = subprocess.run([dep.name, version_flag], capture_output=True)
    if output.returncode == 0:
        stdout = output.stdout.decode("utf-8")
        version_found = search("\d+(\.\d+)*", stdout)
        if version_found:
            ver_str = version_found.group(0)
            version = version_string_to_tuple(ver_str)
            if dep.operation == Op.EXACT:
                if dep.version == version:
                    print(f"'{dep.name} {ver_str}' found")
                else:
                    print(
                        f"'{dep.name} {ver_str}' found, but exact version '{dep.ver_str}' is required"
                    )
            elif dep.operation == Op.MIN:
                if dep.version <= version:
                    print(f"'{dep.name} {ver_str}' found")
                else:
                    print(
                        f"'{dep.name} {ver_str}' found, but minimum version '{dep.ver_str}' is required"
                    )


def check_dependencies_list(deps: List[str]) -> None:
    """Check list of dependencies and prints out if found"""
    for dep in map(parse_dependencies, deps):
        check_dependency(dep)


def check_dependencies(args) -> None:
    """"""
    path = Path(args.dependencies_file)
    try:
        with path.open() as f:
            lines = f.readlines()
    except FileNotFoundError as file_not_found:
        print(f"File '{path}' does not exist")
        exit(1)

    # filter out comment lines and empty lines
    filtered_lines = (line for line in lines if not search("^\s*#|^\s*$", line))

    # At the mo, dependencies file is very constrained
    check_dependencies_list(filtered_lines)
