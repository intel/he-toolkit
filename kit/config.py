# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module for dealing with the hekit configuration file"""

from os import path
from typing import NamedTuple
from toml import load


class Config(NamedTuple):
    """Represents a config"""

    config_filename: str
    repo_location: str


def load_config(filename: str):
    """Load a config file in TOML format"""
    expand = path.expanduser  # alias
    expanded_filename = expand(filename)
    toml_dict = load(expanded_filename)
    toml_dict = {k: expand(v) for k, v in toml_dict.items()}
    # deref kwargs this way, get exceptions unknown key for free
    return Config(expanded_filename, **toml_dict)
