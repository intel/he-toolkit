# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

""" This module provides utility functions for importing and registering subparsers.
"""
from pathlib import Path
from sys import modules
from typing import List
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from kit.utils.constants import Constants, PluginsConfig, PluginState
from kit.utils.tab_completion import get_plugins_by_state
from kit.utils.typing import PathType
from kit.utils.files import files_in_dir, load_toml


def register_subparser(subparsers) -> None:
    """Register surparsers"""
    for func in discover_subparsers_kit(
        ["commands", "tools"], Constants.HEKIT_ROOT_DIR / "kit"
    ):
        func(subparsers)

    for func in discover_subparsers_plugins(
        get_plugins_by_state(PluginState.ENABLE), PluginsConfig.ROOT_DIR
    ):
        func(subparsers)


def import_from_source_file(module_name, file_path):
    """Importing a source file directly"""
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def discover_subparsers_plugins(module_dirs: List[str], kit_root: PathType):
    """Import modules in module_dirs, and discover and return a generator of set_.*_subparser functions"""
    try:
        plugin_config = load_toml(PluginsConfig.FILE)[PluginsConfig.KEY]
    except (FileNotFoundError, KeyError):
        return

    for module_dir in module_dirs:
        fname = plugin_config[module_dir]["start"]
        expected_file = f"{kit_root}/{module_dir}/{fname}"
        if not Path(expected_file).exists():
            continue
        imported_module = import_from_source_file(f"{fname[:-3]}", expected_file)
        funcs = (
            getattr(imported_module, funcname)
            for funcname in dir(imported_module)
            if funcname.startswith("set_") and funcname.endswith("_subparser")
        )
        yield from funcs


def discover_subparsers_kit(module_dirs: List[str], kit_root: PathType):
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
