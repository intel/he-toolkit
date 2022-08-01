# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module provides functions to list files and directories."""

from os import walk
from typing import Callable, List
from enum import Enum
from pathlib import Path
from kit.utils.typing import PathType


class FileType(Enum):
    """Categories of files"""

    DIRS = 1
    FILES = 2


def files_in_dir(
    path: PathType, cond: Callable = None, ftype: FileType = FileType.FILES
) -> List[str]:
    """Returns a list of filenames in the directory given by path. Can be filtered by cond"""
    try:
        filenames = next(walk(path))[ftype.value]
        if cond is None:
            return sorted(filenames)
        return sorted(filter(cond, filenames))
    except StopIteration:
        return []


def list_dirs(path: PathType) -> List[str]:
    """Return list of directories in path."""
    return files_in_dir(path, ftype=FileType.DIRS)


def create_default_workspace(dir_path: str = "~") -> Path:
    """Create the directory ~/.hekit"""
    workspace_path = Path(dir_path).expanduser() / ".hekit"
    workspace_path.mkdir(exist_ok=True)
    return workspace_path
