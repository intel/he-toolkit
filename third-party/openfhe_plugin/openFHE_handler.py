# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from toml import load
from typing import Union, Dict, Any
from subprocess import run  # nosec B404
from shlex import split

PathType = Union[str, Path]
TomlDict = Dict[str, Any]


def load_toml(file_name: PathType) -> TomlDict:
    """Load a toml file and return its content as a dict"""
    file_path = Path(file_name).expanduser()

    if not file_path.exists():
        raise FileNotFoundError(f"File '{file_name}' not found")

    if file_path.is_symlink():
        raise TypeError(f"The  file {file_path.name} cannot be a symlink")

    return load(file_path)


def config_openfhe(args) -> None:
    settings = load_toml(args.config_file)["config"]

    if settings["build_openfhe_release"]:
        print("Unsupported build type.")
        return

    plugin_path = "~/.hekit/plugins/openfhe/recipes"
    recipe_file = "openfhe-hexl.toml" if settings["build_hexl"] else "openfhe.toml"
    recipe_arg = f'openfhe_dev_version={settings["openfhe_dev_version"]},openfhe_hexl_version={settings["openfhe_hexl_version"]}'
    cmd = f'hekit install {plugin_path}/{recipe_file} --recipe_arg "{recipe_arg}"'
    print(cmd)

    run(split(cmd), encoding="utf-8")  # nosec B603


def set_openfhe_subparser(subparsers):
    parser = subparsers.add_parser("openfhe", description="OpenFHE configurator")
    parser.add_argument(
        "--config_file",
        metavar="config-file",
        default="~/.hekit/plugins/openfhe/config.toml",
        help="TOML file with OpenFHE configuration settings",
    )
    parser.set_defaults(fn=config_openfhe)
