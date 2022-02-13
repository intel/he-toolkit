# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
from dataclasses import dataclass
from enum import Enum

#        # load previous from info file
#        try:
#            with open(f"{self._location}/hekit.info") as info_file:
#                self._info_file = toml.load(info_file)
#        except FileNotFoundError:
#            self._info_file = {"status": {"fetch": "", "build": "", "install": ""}}


class StageStatus(Enum):
    """"""

    SUCCESS = "success"
    FAILURE = "failure"
    UNKNOWN = "unknown"
    UNINIT = "uninit"


@dataclass
class InfoFile:
    """"""

    _status: dict

    def load_toml(filepath: str) -> None:
        """"""
        info = toml.load()
        self._status = info["status"]

    def save_toml(filepath: str) -> None:
        """"""
        with open(filepath, "w") as info_file:
            toml.dump({"status": self._status}, info_file)

    def stage_status(stage: str) -> StageStatus:
        """"""
        status_str = self._status[stage]
        return StageStatus(status_str)
