# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Module for Config helper object"""


from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

import toml
from ptxt import Params


class ConfigError(Exception):
    """Errors related to configuration"""


@dataclass(frozen=True)
class Config:
    """The configuration of the encoded data"""

    params: Params
    columns: int
    segments: int
    encodings: Dict[str, str]
    composites: Dict[str, int]

    @classmethod
    def from_toml(cls, filename: str, params_only: bool = False) -> Config:
        """Reads in a params file equiv a simple TOML file"""
        with open(filename, encoding="UTF-8") as f:
            data: Dict = toml.load(f)

        # params
        params_data = data["params"]
        m, p = params_data["m"], params_data["p"]
        params = Params(m, p)

        # config
        config_data = data["config"]
        columns = config_data["columns"]
        segments = config_data["segments"]

        # sanity check
        if params.nslots % segments != 0:
            raise ConfigError(
                f"Segmentation divisor '{segments}' does not divide number of slots '{params.nslots}'"
            )

        if params_only is True:
            return cls(
                params=params,
                columns=columns,
                segments=segments,
                encodings=None,
                composites=None,
            )

        # column policies
        encodings = data["columns"]["encoding"]
        composites = data["columns"]["composite"]
        return cls(
            columns=columns,
            segments=segments,
            params=params,
            encodings=encodings,
            composites=composites,
        )
