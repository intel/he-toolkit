import os
from pathlib import Path
from shutil import copyfile


def create_backup(path: str):
    """"""
    copyfile(path, f"{path}.hekit.bak")


def remove_from_bash_profile(path: str):
    """"""


def write_to_bash_profile(path: str):
    """Config bash init file to know about hekit"""
    start_tag = "# >>> hekit start >>>\n"
    end_tag = "# <<<  hekit end  <<<\n"
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
        raise NotImplemented
        bash_profile = "~/.bash_profile"
        remove_from_bash_profile(bash_profile)
        write_to_bash_profile(bash_profile)
    elif active_shell_path == "zsh":
        raise NotImplemented
    else:
        raise ValueError(f"Unknown shell '{active_shell_path}'")
