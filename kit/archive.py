# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""Provides utility function to archive and compress directories and files"""

import tarfile
from pathlib import Path
from typing import Iterable


def archive_and_compress(
    name: str, filepaths: Iterable[str], root: str, exist_ok: bool = False
) -> None:
    """Archive and compress files and directories into tar.gz file"""
    root = Path(root if root else ".")
    # x:gz raises FileExistsError if file exists
    mode = "w:gz" if exist_ok else "x:gz"
    with tarfile.open(name, mode) as tar:
        for filepath in filepaths:
            tar.add(root / filepath, arcname=filepath)
