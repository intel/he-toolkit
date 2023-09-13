# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module creates a default config file and modifies the shell init file to know about hekit"""

from os import environ as environment
from pathlib import Path
from shutil import copyfile
from filecmp import cmp as same_files

from kit.utils.constants import Constants
from kit.utils.files import create_default_workspace, dump_toml, file_exists
from kit.utils.yes import is_yes


class Tags:
    """Defines opening and closing tags to be added in the shell init file"""

    start_tag: str = "# >>> hekit start >>>\n"
    end_tag: str = "# <<<  hekit end  <<<\n"


def create_backup(path: Path, ext: str = ".hekit.bak") -> Path:
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
            f.writelines(lines_to_write)
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
    lines = ["\n", content, "\n"]
    with path.open("a") as rc_file:
        rc_file.writelines(lines)


def select_rc_file(*potential_files: str) -> Path:
    """Return the first startup file's name (expanded) for a file that exists"""
    for filepath in map(Path, potential_files):
        rc_file = filepath.expanduser().resolve()
        if file_exists(rc_file):
            return rc_file

    raise FileNotFoundError(f"None of the files '{potential_files}' exist")


def get_shell_rc_file() -> tuple[str, Path]:
    """Return the correct shell and file to add shell commands"""
    active_shell_path = Path(environment["SHELL"]).name

    if active_shell_path == "bash":
        rc_file = select_rc_file("~/.bash_profile", "~/.bashrc")
    elif active_shell_path == "zsh":
        rc_file = select_rc_file("~/.zprofile", "~/.zshrc")
    else:
        raise ValueError(f"Unknown shell '{active_shell_path}'")

    return active_shell_path, rc_file


def create_default_config(dir_path: Path) -> None:
    """Create default config file in ~/.hekit,
    when the user sets the default_config flag"""
    # Setup config file
    default_config_path = dir_path / "default.config"
    if file_exists(default_config_path):
        print(f"{default_config_path} file already exists")
    else:
        line = f'repo_location = "{dir_path}/components"\n'
        with default_config_path.open("w", encoding="utf-8") as f:
            f.write(line)
        print(f"{default_config_path} created")


def create_plugin_data(dir_path: Path) -> None:
    """Create the directory ~/.hekit/plugins"""
    plugins_path = dir_path / "plugins"
    plugins_path.mkdir(exist_ok=True)

    # Setup plugin file
    plugin_file_path = plugins_path / "plugins.toml"
    if file_exists(plugin_file_path):
        print(f"{plugin_file_path} file already exists")
    else:
        plugin_data: dict = {"plugins": {}}
        dump_toml(plugin_file_path, plugin_data)
        print(f"{plugin_file_path} created")


def get_rc_new_lines(active_shell: str) -> str:
    """Return the lines that will be added to the rc file"""
    # 1-Add hekit directory as part of environmental variable PATH
    export_line = f"export HEKITPATH={Constants.HEKIT_ROOT_DIR}\n"
    path_line = "PATH=$PATH:$HEKITPATH\n"

    # 2-Register hekit link and hekit.py script to enable tab completion
    pre_eval_lines = (
        "autoload -U bashcompinit\nbashcompinit\n" if active_shell == "zsh" else ""
    )
    eval_lines = (
        'if [ -n "$(type -p register-python-argcomplete)" ]; then\n'
        '  eval "$(register-python-argcomplete hekit)"\n'
        "fi\n"
    )

    return "".join(
        [
            Tags.start_tag,
            export_line,
            path_line,
            pre_eval_lines,
            eval_lines,
            Tags.end_tag,
        ]
    )


def init_hekit(args) -> None:
    """Initialize hekit"""
    if args.default_config:
        dir_path = create_default_workspace()
        create_default_config(dir_path)
        create_plugin_data(dir_path)

    active_shell, rc_path = get_shell_rc_file()
    rc_new_content = get_rc_new_lines(active_shell)

    user_answer = input(
        f"The hekit init command will update the file {rc_path} to append the following lines:\n\n"
        f"{rc_new_content}\n"
        "NOTE: a backup file will be created before updating it.\n"
        "Do you want to continue with this action? (y/n) "
    )
    if not is_yes(user_answer):
        print(
            "Please execute the following actions manually:\n"
            f"1. Open the file {rc_path} in an editor\n"
            "2. Add the lines shown in the previous message\n"
            f"3. Source your shell config file with: source {rc_path}"
        )
        return

    # Backup the shell config file
    rc_backup_file = create_backup(rc_path)
    print("Backup file created at", rc_backup_file)

    # Remove current hekit section, if it exists
    remove_from_rc(rc_path)
    # Add new lines in the rc_file:
    append_to_rc(rc_path, rc_new_content)

    # Instructions for user
    print("Please source your shell config file as follows\n" f"source {rc_path}")


def set_init_subparser(subparsers) -> None:
    """create the parser for the 'init' command"""
    parser_init = subparsers.add_parser("init", description="initialize hekit")
    parser_init.add_argument(
        "--default-config", action="store_true", help="setup default config file"
    )
    parser_init.set_defaults(fn=init_hekit)
