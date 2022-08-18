# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module defines constants that are used in the version, docker build and new commands"""

from dataclasses import dataclass
from getpass import getuser
from pathlib import Path


@dataclass(frozen=True, init=False)
class Constants:  # pylint: disable=too-many-instance-attributes
    """Defines constants for the he-toolkit"""

    # version and the docker's tags
    user: str = getuser()
    version: str = "2.0.0"
    base_label: str = f"{user}/ubuntu_he_base:{version}"
    toolkit_label: str = f"{user}/ubuntu_he_toolkit:{version}"
    vscode_label: str = f"{user}/ubuntu_he_vscode:{version}"

    # cmake properties
    cmake_min_version: str = "3.13"
    cmake_cxx_standard: str = "17"

    # Plugins
    plugins_root_dir: Path = Path("~/.hekit/plugins/").expanduser()
