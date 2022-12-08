# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Utilities used by the tests"""

import pytest
from pathlib import Path
from subprocess import run
from shlex import split


def create_config_file(path: Path) -> Path:
    config_file = f"{path}/default.config"

    with open(f"{config_file}", "w") as f:
        f.write(f'repo_location = "{path}"\n')

    return config_file


def execute_process(cmd: str) -> str:
    return run(split(cmd), encoding="utf-8", capture_output=True)


@pytest.fixture
def input_files_path() -> Path:
    return Path(__file__).resolve().parent / "input_files"


@pytest.fixture
def hekit_path() -> Path:
    return Path(__file__).resolve().parent.parent / "hekit"
