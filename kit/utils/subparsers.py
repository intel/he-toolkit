# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

""" This module provides utility functions for importing and registering subparsers.
"""

from os import walk
from importlib import import_module
from typing import List, Callable


def files_in_dir(path: str, cond: Callable) -> List[str]:
    """Returns a list of filenames in the directory given by path. Can be filtered by cond"""
    try:
        filenames = next(walk(path))[2]
        if cond is None:
            return filenames
        return list(filter(cond, filenames))
    except StopIteration:
        return []


def discover_subparsers_from(module_dirs: List[str], kit_root: str):
    """Import modules in module_dirs, and discover and return a generator of set_.*_subparser functions"""
    for module_dir in module_dirs:
        filenames = files_in_dir(
            f"{kit_root}/{module_dir}", lambda f: f[0] != "_" and f.endswith(".py")
        )
        imported_modules = (
            import_module(f"{module_dir}.{fname[:-3]}") for fname in filenames
        )
        funcs = (
            getattr(imported_module, funcname)
            for imported_module in imported_modules
            for funcname in dir(imported_module)
            if funcname.startswith("set_") and funcname.endswith("_subparser")
        )
        yield from funcs
