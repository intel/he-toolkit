# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

""" This module provides utility functions for importing and registering subparsers.
"""
from sys import modules
from importlib.util import spec_from_file_location, module_from_spec
from typing import List
from kit.utils.typing import PathType
from kit.utils.files import files_in_dir


def import_from_source_file(module_name, file_path):
    """Importing a source file directly"""
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def discover_subparsers_from(module_dirs: List[str], kit_root: PathType):
    """Import modules in module_dirs, and discover and return a generator of set_.*_subparser functions"""
    for module_dir in module_dirs:
        module_path = f"{kit_root}/{module_dir}"
        filenames = files_in_dir(
            module_path, lambda f: f[0] != "_" and f.endswith(".py")
        )

        imported_modules = (
            import_from_source_file(f"{fname[:-3]}", f"{module_path}/{fname}")
            for fname in filenames
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
