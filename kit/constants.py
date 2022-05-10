# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module defines constants that are used in version and docker build commands"""

from dataclasses import dataclass
from getpass import getuser

@dataclass(frozen=True, init=False)
class Constants:
    """Defines constants as toolkit version and the docker's tags"""

    user: str = getuser()
    version: str = "2.0.0"
    base_label: str = f"{user}/ubuntu_he_base:{version}"
    toolkit_label: str = f"{user}/ubuntu_he_toolkit:{version}"
    vscode_label: str = f"{user}/ubuntu_he_vscode:{version}"
