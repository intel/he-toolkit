# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from os import environ as environment
from pathlib import Path
from shutil import copyfile
from filecmp import cmp as compare_files


class Tags:
    start_tag: str = "# >>> hekit start >>>\n"
    end_tag: str = "# <<<  hekit end  <<<\n"


def create_backup(path: str, ext: str = ".hekit.bak") -> str:
    """"""
    path = Path(path).expanduser().resolve()
    backup = path.with_suffix(ext)
    copyfile(path, backup)
    # Sanity check - we really need to guarantee we copied the file
    if compare_files(path, backup, shallow=False) == False:
        raise ValueError("Backup file does not match original")
    return backup


def remove_from_rc(path: str) -> None:
    """Remove hekit section"""
    path = Path(path).expanduser().resolve()
    with path.open() as f:
        lines = f.readlines()  # slurp

    start_tag_count = lines.count(Tags.start_tag)
    end_tag_count = lines.count(Tags.end_tag)

    if start_tag_count == 0 and end_tag_count == 0:
        return  # nothing to do
    elif start_tag_count == 1 and end_tag_count == 1:
        start_index, end_index = lines.index(Tags.start_tag), lines.index(Tags.end_tag)
        lines_to_write = (
            line for i, line in enumerate(lines) if not start_index <= i <= end_index
        )
        with path.open("w") as f:
            for line in lines_to_write:
                f.write(line)
    elif start_tag_count > 1 or end_tag_count > 1:
        raise ValueError("More than one each of hekit tags")
    else:
        raise ValueError(
            f"Not an acceptable number of hekit tags: '{start_tag_count}, {end_tag_count}'"
        )


def append_to_rc(path: str, content: str) -> None:
    """Config bash init file to know about hekit"""
    shell_rc_path = Path(path).expanduser().resolve()

    if content[:-1] != "\n":  # add newline if not there
        content += "\n"

    if not shell_rc_path.exists():
        raise FileNotFoundError(shell_rc_path)

    # newline to not accidentally mix with existing content
    # newline to end as courtesy to space our code
    lines = ["\n", Tags.start_tag, content, Tags.end_tag, "\n"]
    with shell_rc_path.open("a") as rc_file:
        for line in lines:
            rc_file.write(line)


def init_hekit(args):
    """Initialize hekit"""
    active_shell_path = Path(environment["SHELL"]).name

    if active_shell_path == "bash":
        rc_file = "~/.bash_profile"
    elif active_shell_path == "zsh":
        rc_file = ""
    else:
        raise ValueError(f"Unknown shell '{active_shell_path}'")

    rc_backup_file = create_backup(rc_file)
    print("Backup file created at", rc_backup_file)
    remove_from_rc(rc_file)
    append_to_rc(rc_file, content=f"PATH={args.hekit_root_dir}:$PATH")
    print("Please, source your shell init file as follows,\n" f"source {rc_file}")
