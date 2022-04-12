# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from os import environ as environment
from pathlib import Path
from shutil import copyfile
from filecmp import cmp as same_files


class Tags:
    start_tag: str = "# >>> hekit start >>>\n"
    end_tag: str = "# <<<  hekit end  <<<\n"


def file_exists(file: Path) -> bool:
    """ Wrapper to check if file exists because Path.exists() cannot be mocked
    directly due to being used internally by pytest creating some clash"""
    return file.exists()


def get_expanded_path(path: str) -> Path:
    """Return the expanded path of a file if it exists,
    otherwise raise an exception"""
    path_file = Path(path).expanduser().resolve()
    if not file_exists(path_file):
        raise FileNotFoundError(path_file)

    return path_file


def create_backup(path: Path, ext: str = ".hekit.bak") -> str:
    """Create a backup of the input file"""
    backup = path.with_suffix(ext)
    copyfile(path, backup)
    # Sanity check - we really need to guarantee we copied the file
    if not same_files(path, backup, shallow=False):
        raise ValueError("Backup file does not match original")
    return backup


def remove_from_rc(path: Path) -> None:
    """Remove hekit section"""
    with path.open() as f:
        lines = f.readlines()  # slurp

    start_tag_count = lines.count(Tags.start_tag)
    end_tag_count = lines.count(Tags.end_tag)

    if start_tag_count == 0 and end_tag_count == 0:
        return  # nothing to do

    if start_tag_count == 1 and end_tag_count == 1:
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


def append_to_rc(path: Path, content: str) -> None:
    """Config bash init file to know about hekit"""
    if content[:-1] != "\n":  # add newline if not there
        content += "\n"

    # newline to not accidentally mix with existing content
    # newline to end as courtesy to space our code
    lines = ["\n", Tags.start_tag, content, Tags.end_tag, "\n"]
    with path.open("a") as rc_file:
        for line in lines:
            rc_file.write(line)


def get_rc_file() -> str:
    """ Return the correct file to add shell commands"""
    active_shell_path = Path(environment["SHELL"]).name

    if active_shell_path == "bash":
        # if bash_profile file does not exist, try bashrc file
        rc_file = Path("~/.bash_profile").expanduser().resolve()
        if not file_exists(rc_file):
            rc_file = "~/.bashrc"
    # TODO add support for other popular shells
    #    elif active_shell_path == "zsh":
    #        rc_file = ""
    else:
        raise ValueError(f"Unknown shell '{active_shell_path}'")

    return rc_file


def create_default_config() -> None:
    """Create default config file in ~/.hekit,
    when the user sets the default_config flag"""
    # Create ~/.hekit, this should always exist
    dir_path = "~/.hekit"
    Path(dir_path).expanduser().mkdir(exist_ok=True)

    # Setup config file
    file_path = f"{dir_path}/default.config"
    default_config_path = Path(file_path).expanduser()
    if file_exists(default_config_path):
        print(f"{file_path} file already exists")
    else:
        line = f'repo_location = "{dir_path}/components"\n'
        with default_config_path.open("w", encoding="utf-8") as f:
            f.write(line)
        print(f"{file_path} created")


def init_hekit(args):
    """Initialize hekit"""
    if args.default_config:
        create_default_config()

    # Backup the shell init file
    rc_file = get_rc_file()
    rc_path = get_expanded_path(rc_file)
    rc_backup_file = create_backup(rc_path)
    print("Backup file created at", rc_backup_file)

    # Remove current hekit section, if it exists
    remove_from_rc(rc_path)

    # Add new lines in the rc_file:
    # 1-Add hekit directory as part of environmental variable PATH
    path_line = f"PATH={args.hekit_root_dir}:$PATH"
    # 2-Register hekit link and hekit.py script to enable tab completion
    eval_lines = (
        "if [ -n $(type -p register-python-argcomplete) ]; then\n"
        '  eval "$(register-python-argcomplete hekit.py hekit)"\n'
        "fi\n"
    )
    content = "\n".join([path_line, eval_lines])
    append_to_rc(rc_path, content)

    # Instructions for user
    print("Please, source your shell init file as follows")
    print(f"source {rc_file}")


def set_init_subparser(subparsers, hekit_root_dir):
    """create the parser for the 'init' command"""
    parser_init = subparsers.add_parser("init", description="initialize hekit")
    parser_init.add_argument(
        "--default-config", action="store_true", help="setup default config file"
    )
    parser_init.set_defaults(fn=init_hekit, hekit_root_dir=hekit_root_dir)