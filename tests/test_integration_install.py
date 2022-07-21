# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from os import getcwd, chdir
from pathlib import Path
from subprocess import run, check_output, STDOUT, PIPE

from kit.hekit import main
from kit.commands.list_cmd import list_components, _SEP_SPACES
from kit.commands.remove import remove_components
from kit.commands.install import install_components

# Due to install command changes current directory,
# the other commands need to restore the current path
cwd_test = getcwd()


def test_install_fetch(tmp_path):
    """Arrange"""
    config_file = f"{tmp_path}/default.config"
    tests_path = Path(__file__).resolve().parent

    args = ["echo", f'repo_location = "{tmp_path}"']
    with open(f"{config_file}", "w") as f:
        run(args, stdout=f)

    args = [
        "hekit",
        "--config",
        f"{config_file}",
        "fetch",
        f"{tests_path}/input_files/test.toml",
        "--recipe_arg",
        '"name=1.2.3,build=build"',
    ]
    output = run(args, capture_output=True)
    assert "[GIT] Cloning into 'hexl'..." in output.stdout.decode("utf-8")

    args = ["hekit", "--config", f"{config_file}", "list"]
    output = run(args, capture_output=True)
    assert "hexl   1.2.3   success                         " in output.stdout.decode(
        "utf-8"
    )

    args = [
        "hekit",
        "--config",
        f"{config_file}",
        "build",
        f"{tests_path}/input_files/test.toml",
        "--recipe_arg",
        '"name=1.2.3,build=build"',
    ]
    output = run(args, capture_output=True)
    assert "build" in output.stdout.decode("utf-8")

    args = ["hekit", "--config", f"{config_file}", "list"]
    output = run(args, capture_output=True)
    assert "hexl   1.2.3   success    success              " in output.stdout.decode(
        "utf-8"
    )

    args = [
        "hekit",
        "--config",
        f"{config_file}",
        "install",
        f"{tests_path}/input_files/test.toml",
        "--recipe_arg",
        '"name=1.2.3,build=build"',
    ]
    output = run(args, capture_output=True)
    assert "build" in output.stdout.decode("utf-8")

    args = ["hekit", "--config", f"{config_file}", "list"]
    output = run(args, capture_output=True)
    assert "hexl   1.2.3   success    success    success   " in output.stdout.decode(
        "utf-8"
    )

    args = ["hekit", "--config", f"{config_file}", "remove", "hexl", "1.2.3"]
    output = run(args, capture_output=True)
    assert "build" not in output.stdout.decode("utf-8")

    """Act"""

    """Assert"""


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, fn, upto_stage):
        self.tests_path = Path(__file__).resolve().parent
        self.version = False
        self.component = "hexl"
        self.instance = "1.2.3"
        self.config = f"{self.tests_path}/input_files/default.config"
        self.recipe_file = f"{self.tests_path}/input_files/test.toml"
        self.fn = fn
        self.upto_stage = upto_stage
        self.force = False
        self.all = False
        self.y = True
        # back substitution
        self.recipe_arg = {"name": self.instance}
        self.toml_arg_version = self.instance
        self.toml_arg_build = "build"


@pytest.fixture
def args_fetch():
    return MockArgs(install_components, "fetch")


@pytest.fixture
def args_build():
    return MockArgs(install_components, "build")


@pytest.fixture
def args_install():
    return MockArgs(install_components, "install")


@pytest.fixture
def args_list():
    return MockArgs(list_components, "")


@pytest.fixture
def args_remove():
    return MockArgs(remove_components, "")


@pytest.fixture
def restore_pwd():
    global cwd_test
    chdir(cwd_test)


def get_width_and_arg1(comp: str, inst: str, separation_spaces: int = _SEP_SPACES):
    width = 10
    width_comp = len(comp) + separation_spaces
    width_inst = len(inst) + separation_spaces

    return width, f"{comp:{width_comp}} {inst:{width_inst}}"
