# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from os import environ as environment
from pathlib import Path
from shutil import copyfile
from filecmp import cmp as compare_files
from importlib import util


class Tags:
    start_tag: str = "# >>> hekit start >>>\n"
    end_tag: str = "# <<<  hekit end  <<<\n"


def check_file_exist(path: str):
    """Return the expanded path of a file if it exists,
    otherwise it rises an exception"""
    path_file = Path(path).expanduser().resolve()
    if not path_file.exists():
        raise FileNotFoundError(path_file)

    return path_file


def create_backup(path: str, ext: str = ".hekit.bak") -> str:
    """Create a backup of the input file"""
    path = check_file_exist(path)
    backup = path.with_suffix(ext)
    copyfile(path, backup)
    # Sanity check - we really need to guarantee we copied the file
    if compare_files(path, backup, shallow=False) == False:
        raise ValueError("Backup file does not match original")
    return backup


def remove_from_rc(path: str) -> None:
    """Remove hekit section"""
    path = check_file_exist(path)
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
    shell_rc_path = check_file_exist(path)

    if content[:-1] != "\n":  # add newline if not there
        content += "\n"

    # newline to not accidentally mix with existing content
    # newline to end as courtesy to space our code
    lines = ["\n", Tags.start_tag, content, Tags.end_tag, "\n"]
    with shell_rc_path.open("a") as rc_file:
        for line in lines:
            rc_file.write(line)


def get_rc_file():
    """ Return the correct file to add shell commands"""
    active_shell_path = Path(environment["SHELL"]).name

    if active_shell_path == "bash":
        # if bash_profile file does not exist, try bashrc file
        rc_file = "~/.bash_profile"
        if not Path(rc_file).expanduser().resolve().exists():
            rc_file = "~/.bashrc"
    elif active_shell_path == "zsh":
        rc_file = ""
    else:
        raise ValueError(f"Unknown shell '{active_shell_path}'")

    return rc_file


def init_hekit(args):
    """Initialize hekit"""
    rc_file = get_rc_file()
    rc_backup_file = create_backup(rc_file)
    print("Backup file created at", rc_backup_file)
    remove_from_rc(rc_file)

    # New lines that will be added in the rc_file:
    # 1-Add hekit directory as part of environmental variable PATH
    content = f"PATH={args.hekit_root_dir}:$PATH"

    # 2-Register hekit link and hekit.py script to enable tab completion
    if not util.find_spec("argcomplete") == None:
        register_py = f'eval "$(register-python-argcomplete hekit.py)"'
        register_link = f'eval "$(register-python-argcomplete hekit)"'
        content = "\n".join([content, register_py, register_link])

    append_to_rc(rc_file, content)
    print("Please, source your shell init file as follows,\n" f"source {rc_file}")
