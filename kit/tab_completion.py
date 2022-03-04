# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from config import load_config
from command_list import list_dirs


def enable_tab_completion(parser):
    """Tab completion is an optional feature, this means that
    hekit can be executed without enabling this functionality.
    But if the user installs argcomplete and registers the
    hekit script, tab completion will be available"""
    try:
        from argcomplete import autocomplete

        autocomplete(parser)
    except ImportError:
        pass


def components_completer(prefix, parsed_args, **kwargs):
    """Returns the components that were installed with the hekit"""
    config = load_config(parsed_args.config)
    return list_dirs(config.repo_location)


def instances_completer(prefix, parsed_args, **kwargs):
    """Returns the instances of a component that
    was installed with the hekit"""
    config = load_config(parsed_args.config)
    comp_name_path = f"{config.repo_location}/{parsed_args.component}"
    return list_dirs(comp_name_path)
