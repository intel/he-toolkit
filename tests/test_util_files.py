# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest

from pathlib import Path
from kit.utils.files import files_in_dir, list_dirs, create_default_workspace, load_toml


def test_files_in_dir_commands_filter_py(get_toolkit_path):
    exp_files = {
        "docker_build.py",
        "check_deps.py",
        "install.py",
        "init.py",
        "remove.py",
        "new.py",
        "list_cmd.py",
        "plugin.py",
    }
    module = get_toolkit_path / "kit" / "commands"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    filenames = files_in_dir(module, filter)
    assert exp_files == set(filenames)


def test_files_in_dir_commands_filter_None(get_toolkit_path):
    exp_files = {
        "docker_build.py",
        "__init__.py",
        "check_deps.py",
        "install.py",
        "init.py",
        "remove.py",
        "new.py",
        "list_cmd.py",
        "plugin.py",
    }
    module = get_toolkit_path / "kit" / "commands"
    filter = None

    filenames = files_in_dir(module, filter)
    assert exp_files == set(filenames)


def test_files_in_dir_tools_filter_py(get_toolkit_path):
    exp_files = {"healg.py"}
    module = get_toolkit_path / "kit" / "tools"
    filter = lambda f: f[0] != "_" and f.endswith(".py")

    filenames = files_in_dir(module, filter)
    assert exp_files == set(filenames)


def test_list_dirs(get_toolkit_path):
    exp_files = ["utils", "tools", "commands"]
    module = get_toolkit_path / "kit"

    directories = list_dirs(module)
    assert exp_files[0] in set(directories)
    assert exp_files[1] in set(directories)
    assert exp_files[2] in set(directories)


def test_create_default_config_file_created(mocker):
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    create_default_workspace()
    mock_mkdir.assert_called_once()


def test_load_toml(get_toolkit_path):
    file = f"{get_toolkit_path}/tests/input_files/default.config"
    act_dict = load_toml(file)
    assert "~/.hekit_test/components" == act_dict["repo_location"]


def test_load_toml_symlink(get_toolkit_path):
    file = f"{get_toolkit_path}/tests/input_files/default_symlink.config"
    with pytest.raises(Exception) as exc_info:
        load_toml(file)

    assert "default_symlink.config cannot be a symlink" in str(exc_info.value)


@pytest.fixture
def get_toolkit_path():
    return Path(__file__).resolve().parent.parent
