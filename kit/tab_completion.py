#! /usr/bin/python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from config import load_config
from command_list import get_components, get_instances


def enable_tab_completion(parser):
    try:
        from argcomplete import autocomplete

        autocomplete(parser)
    except ImportError:
        pass


def components_completer(prefix, parsed_args, **kwargs):
    config = load_config(parsed_args.config)
    return get_components(config.repo_location)


def instances_completer(prefix, parsed_args, **kwargs):
    config = load_config(parsed_args.config)
    comp_name_path = f"{config.repo_location}/{parsed_args.component}"
    return get_instances(comp_name_path)
