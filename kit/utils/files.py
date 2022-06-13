# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from os import walk
from typing import Callable, List
from enum import Enum


class FileType(Enum):
    DIRS = 1
    FILES = 2


def files_in_dir(
    path: str, cond: Callable = None, ftype: FileType = FileType.FILES
) -> List[str]:
    """Returns a list of filenames in the directory given by path. Can be filtered by cond"""
    try:
        filenames = next(walk(path))[ftype.value]
        if cond is None:
            return sorted(filenames)
        return sorted(filter(cond, filenames))
    except StopIteration:
        return []


def list_dirs(path: str) -> List[str]:
    """Return list of directories in path."""
    return files_in_dir(path, ftype=FileType.DIRS)
