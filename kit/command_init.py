# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
from shutil import copyfile

_start_tag = "# >>> hekit start >>>\n"
_end_tag = "# <<<  hekit end  <<<\n"


def create_backup(path: str, ext: str = ".hekit.bak"):
    """"""
    copyfile(path, f"{path}.{ext}")


def remove_from_bash_profile(path: str):
    """Remove hekit section"""
    with Path(path).open() as f:
        lines = f.readlines()  # slurp

    start_tag_count = lines.count(_start_tag)
    end_tag_count = lines.count(_end_tag)

    if start_tag_count == 0 and end_tag_count == 0:
        return  # nothing to do
    elif start_tag_count == 1 and end_tag_count == 1:
        start_index, end_index = lines.index(_start_tag), lines.index(_end_tag)
        lines_to_write = (
            line for line in enumerate(lines) if not start_index <= i <= end_index
        )
        with Path(path).open() as f:
            for line in lines_to_write:
                f.write(line)
    elif start_tag_count > 1 or end_tag_count > 1:
        raise ValueError("More than one each of hekit tags")
    else:
        raise ValueError(
            f"Not an acceptable number of hekit tags: '{start_tag_count}, {end_tag_count}'"
        )


def write_to_rc(path: str):
    """Config bash init file to know about hekit"""
    shell_rc_path = Path(path)
    with shell_rc_path.open() as rc_file:
        lines = rc_file.readlines()  # slurp

    lines = [start_tag, end_tag]
    with shell_rc_path.open("a") as rc_file:
        for line in lines:
            rc_file.write(line)


def init_hekit(args, rc_path: str):
    """Initialize hekit"""
    active_shell_path = Path(os.environ["SHELL"])

    if active_shell_path == "bash":
        rc_file = "~/.bash_profile"
    elif active_shell_path == "zsh":
        rc_file = ""
    else:
        raise ValueError(f"Unknown shell '{active_shell_path}'")
