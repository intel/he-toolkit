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
    version: str = "2.1.0"
    base_label: str = f"{user}/ubuntu_he_base:{version}"
    toolkit_label: str = f"{user}/ubuntu_he_toolkit:{version}"
    vscode_label: str = f"{user}/ubuntu_he_vscode:{version}"
    custom_label: str = f"{user}/ubuntu_he_%s:{version}"

    # python version
    python_version_tuple = (3, 10)
    python_version_string = "3.10"

    # cmake properties
    cmake_min_version: str = "3.22"
    cmake_cxx_standard: str = "17"

    # Root directory
    HEKIT_ROOT_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Docker directory
    HEKIT_DOCKER_DIR: Path = Path(__file__).resolve().parent.parent.parent / "docker"

    # hekit core commands
    HEKIT_COMMANDS = {
        "check-dependencies",
        "docker-build",
        "init",
        "install",
        "build",
        "fetch",
        "list",
        "new",
        "plugins",
        "remove",
        "algebras",
        "gen-primes",
    }


@dataclass(frozen=True, init=False)
class PluginState:
    """Define the possible state of a plugin"""

    ENABLE: str = "enabled"
    DISABLE: str = "disabled"


@dataclass(frozen=True, init=False)
class PluginsConfig:
    """Define the attributes of the config file for plugins"""

    ROOT_DIR: Path = Path("~/.hekit/plugins/").expanduser()
    FILE: Path = ROOT_DIR / "plugins.toml"
    KEY: str = "plugins"
