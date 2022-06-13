# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

""" This module provides utility functions for importing and registering subparsers.
"""

from importlib import import_module
from typing import List, Callable
from kit.utils.typing import PathType
from kit.utils.files import files_in_dir


def discover_subparsers_from(module_dirs: List[str], kit_root: PathType):
    """Import modules in module_dirs, and discover and return a generator of set_.*_subparser functions"""
    for module_dir in module_dirs:
        filenames = files_in_dir(
            f"{kit_root}/{module_dir}", lambda f: f[0] != "_" and f.endswith(".py")
        )
        imported_modules = (
            import_module(f"kit.{module_dir}.{fname[:-3]}") for fname in filenames
        )
        funcs = (
            getattr(imported_module, funcname)
            for imported_module in imported_modules
            for funcname in dir(imported_module)
            if funcname.startswith("set_") and funcname.endswith("_subparser")
        )
        yield from funcs


def validate_input(input_value: str) -> str:
    """Raises an exception if input has non-printable characters"""
    if not input_value.isprintable():
        raise ValueError("Input is not valid due to non-printable characters")

    return input_value
