# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module provides tab completion if the dependencies are installed"""

from commands.list_cmd import list_dirs
from utils.config import load_config  # pylint: disable=no-name-in-module

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
    prefix, parsed_args, **kwargs
):  # pylint: disable=unused-argument
    """Returns the components that were installed with the hekit"""
    config = load_config(parsed_args.config)
    return list_dirs(config.repo_location)


def instances_completer(
    prefix, parsed_args, **kwargs
):  # pylint: disable=unused-argument
    """Returns the instances of a component that
    was installed with the hekit"""
    config = load_config(parsed_args.config)
    comp_name_path = f"{config.repo_location}/{parsed_args.component}"
    return list_dirs(comp_name_path)
