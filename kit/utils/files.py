# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module provides functions to list files and directories."""

from os import walk
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from toml import load, dump

from kit.utils.typing import PathType

TomlDict = dict[str, Any]


class FileType(Enum):
    """Categories of files"""

    DIRS = 1
    FILES = 2


def file_exists(file: Path) -> bool:
    """Wrapper to check if file exists because Path.exists() cannot be mocked
    directly due to being used internally by pytest creating some clash"""
    return file.exists()


def files_in_dir(
    path: PathType, cond: Optional[Callable] = None, ftype: FileType = FileType.FILES
) -> list[str]:
    """Returns a list of filenames in the directory given by path. Can be filtered by cond"""
    try:
        filenames = next(walk(path))[ftype.value]
        if cond is None:
            return sorted(filenames)
        return sorted(filter(cond, filenames))
    except StopIteration:
        return []


def list_dirs(path: PathType) -> list[str]:
    """Return list of directories in path."""
    return files_in_dir(path, ftype=FileType.DIRS)


def create_default_workspace(dir_path: str = "~") -> Path:
    """Create the directory ~/.hekit"""
    workspace_path = Path(dir_path).expanduser() / ".hekit"
    workspace_path.mkdir(exist_ok=True)
    return workspace_path


def load_toml(file_name: PathType) -> TomlDict:
    """Load a toml file and return its content as a dict"""
    file_path = Path(file_name).expanduser()

    if not file_exists(file_path):
        raise FileNotFoundError(f"File '{file_name}' not found")

    # Note: Path.resolve() cannot be used before checking Path.is_symlink()
    if file_path.is_symlink():
        raise TypeError(f"File {file_path.name} cannot be a symlink")

    return load(file_path)


def dump_toml(file_name: PathType, content: TomlDict) -> None:
    """Write a TOML file"""
    file_path = Path(file_name).expanduser()

    with file_path.open("w", encoding="utf-8") as f:
        dump(content, f)


def dash_to_underscore(name: str) -> str:
    """Return string with dashes changed to underscores."""
    return name.replace("-", "_")
