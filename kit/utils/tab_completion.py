# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module provides tab completion if the dependencies are installed"""

from pathlib import Path
from typing import List
from kit.utils.constants import PluginsConfig, PluginState
from kit.utils.config import load_config, load_toml
from kit.utils.files import list_dirs


try:
    # Tab completion is an optional feature, this means that
    # hekit can be executed without enabling this functionality.
    # But if the user installs argcomplete and registers the
    # hekit script, tab completion will be available
    from argcomplete import autocomplete
except ImportError as e:

    def autocomplete(arg):  # pylint: disable=unused-argument
        """Continue with the execution"""


def enable_tab_completion(parser):
    """Enables tab completion feature if dependencies are fulfilled"""
    autocomplete(parser)


def components_completer(
    prefix, parsed_args, **kwargs  # pylint: disable=unused-argument
) -> List[str]:
    """Returns the components that were installed with the hekit"""
    config = load_config(parsed_args.config)
    return list_dirs(config.repo_location)


def instances_completer(
    prefix, parsed_args, **kwargs  # pylint: disable=unused-argument
) -> List[str]:
    """Returns the instances of a component that
    was installed with the hekit"""
    config = load_config(parsed_args.config)
    comp_name_path = f"{config.repo_location}/{parsed_args.component}"
    return list_dirs(comp_name_path)


def get_plugins_by_state(
    state: str, source_file: Path = PluginsConfig.FILE
) -> List[str]:
    """Return a list of plugins with a specific state"""
    try:
        plugin_dict = load_toml(source_file)[PluginsConfig.KEY]
        return [k for k, v in plugin_dict.items() if v["state"] == state]

    except (FileNotFoundError, KeyError):
        return []


def plugins_enable_completer(
    prefix, parsed_args, **kwargs  # pylint: disable=unused-argument
) -> List[str]:
    """Return a list of plugins that are enabled"""
    return get_plugins_by_state(PluginState.ENABLE)


def plugins_disable_completer(
    prefix, parsed_args, **kwargs  # pylint: disable=unused-argument
) -> List[str]:
    """Return a list of plugins that are disabled"""
    return get_plugins_by_state(PluginState.DISABLE)
