# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Utilities used by the tests"""

import pytest
from pathlib import Path
from subprocess import run
from shlex import split


def create_config_file(path: Path) -> Path:
    config_file = f"{path}/default.config"
    cmd = ["echo", f'repo_location = "{path}"']

    with open(f"{config_file}", "w") as f:
        run(cmd, stdout=f)

    return config_file


def execute_process(cmd: str) -> str:
    out = run(split(cmd), capture_output=True)
    return out.stdout.decode("utf-8"), out.stderr.decode("utf-8")


@pytest.fixture
def input_files_path() -> Path:
    return Path(__file__).resolve().parent / "input_files"


@pytest.fixture
def hekit_path() -> Path:
    return Path(__file__).resolve().parent.parent / "hekit"
