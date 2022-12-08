# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

""" This module provides utility functions for importing and registering subparsers.
"""
from argparse import ArgumentParser
from pathlib import Path
from sys import modules
from typing import Dict, List
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from kit.utils.constants import Constants, PluginsConfig, PluginState
from kit.utils.typing import PathType
from kit.utils.files import files_in_dir, load_toml, dash_to_underscore


ParserDict = Dict[str, ArgumentParser]


def register_subparser(subparsers) -> None:
    """Register surparsers"""
    for func in get_subparsers_kit(
        ["commands", "tools"], Constants.HEKIT_ROOT_DIR / "kit"
    ):
        func(subparsers)

    for func in get_subparsers_plugins(
        get_plugins_start_files(), PluginsConfig.ROOT_DIR
    ):
        func(subparsers)


def import_from_source_file(module_name, file_path):
    """Importing a source file directly"""
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def get_subparsers_plugins(
    plugin_config: Dict[str, str],
    plugin_root: PathType,
):
    """Import plugins in module_dirs, and discover and
    return a generator of set_.*_subparser functions"""
    for plugin_name, start_file in plugin_config.items():
        plugin_dirname = dash_to_underscore(plugin_name)
        expected_file = f"{plugin_root}/{plugin_dirname}/{start_file}"
        if not Path(expected_file).exists():
            continue
        imported_module = import_from_source_file(f"{start_file[:-3]}", expected_file)
        funcs = (
            getattr(imported_module, funcname)
            for funcname in dir(imported_module)
            if funcname.startswith("set_") and funcname.endswith("_subparser")
        )
        yield from funcs


def get_plugin_arg_choices(
    plugin_name: str,
    plugin_root: PathType = PluginsConfig.ROOT_DIR,
) -> List[str]:
    """Return the choices (list of plugin names) of the argument parser"""
    try:
        # Read the TOML file to identify plugin's name and start
        plugin_dirname = dash_to_underscore(plugin_name)
        toml_file = f"{plugin_root}/{plugin_dirname}/plugin.toml"
        plugin_config = load_toml(toml_file)["plugin"]
        plugin_start = {plugin_config["name"]: plugin_config["start"]}

        # Get the function that defines the plugin arguments
        func = next(get_subparsers_plugins(plugin_start, plugin_root))

        # Create a parser to get the argument name
        tmp_parser = ArgumentParser(prog="tmp")
        subparsers = tmp_parser.add_subparsers()
        func(subparsers)

        return list(subparsers.choices.keys())
    except (FileNotFoundError, KeyError):
        return []


def get_plugins_start_files(source_file: Path = PluginsConfig.FILE) -> Dict[str, str]:
    """Returns a dictionary with the start file of each plugin"""
    try:
        plugin_config = load_toml(source_file)[PluginsConfig.KEY]
        return {
            k: v["start"]
            for k, v in plugin_config.items()
            if v["state"] == PluginState.ENABLE
        }
    except (FileNotFoundError, KeyError):
        return {}


def get_subparsers_kit(module_dirs: List[str], kit_root: PathType):
    """Import cmds and tools in module_dirs, and discover and
    return a generator of set_.*_subparser functions"""
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


def get_options_description(parser_choices: ParserDict, width: int) -> str:
    """Return the name and usage of each sub-command"""
    return "\n".join(f"{k:{width}} {v.description}" for k, v in parser_choices.items())
