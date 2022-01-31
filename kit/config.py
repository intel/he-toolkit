# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml

import os
from typing import NamedTuple


class Config(NamedTuple):
    """Represents a config"""

    config_filename: str
    repo_location: str


def load_config(filename: str):
    """Load a config file in TOML format"""
    expand = os.path.expanduser  # alias
    expanded_filename = expand(filename)
    toml_dict = toml.load(expanded_filename)
    toml_dict = {k: expand(v) for k, v in toml_dict.items()}
    # deref kwargs this way, get exceptions unknown key for free
    return Config(expanded_filename, **toml_dict)
