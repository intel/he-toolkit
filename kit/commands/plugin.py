# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the usage of third party plugins"""

from enum import Enum
from pathlib import Path
from shutil import rmtree, copytree
from tarfile import is_tarfile, open as tar_open
from typing import Dict, List
from zipfile import is_zipfile, ZipFile
from toml import loads as toml_loads
from kit.utils.constants import PluginsConfig, PluginState
from kit.utils.files import load_toml, dump_toml
from kit.utils.subparsers import validate_input
from kit.utils.tab_completion import plugins_enable_completer, plugins_disable_completer


ConfigDict = Dict[str, Dict[str, str]]
PluginsDataList = List[Dict[str, str]]


class InvalidPluginError(Exception):
    """InvalidPluginError exception raised for an invalid plugin"""


class PluginType(Enum):
    """Categories of files"""

    DIR = 1
    TAR = 2
    ZIP = 3


def load_plugins_config_file(source_file: Path = PluginsConfig.FILE) -> ConfigDict:
    """Return plugins dictionary"""
    try:
        # Get the plugins data
        return load_toml(source_file)[PluginsConfig.KEY]
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"{str(e)}. Please execute: hekit init --default-config"
        ) from e


def update_plugins_config_file(
    config_dict: ConfigDict, dest_file: Path = PluginsConfig.FILE
) -> None:
    """Save changes in the plugins data"""
    sorted_dict = {PluginsConfig.KEY: dict(sorted(config_dict.items()))}
    dump_toml(dest_file, sorted_dict)


def get_plugin_type(plugin_path: Path) -> PluginType:
    """Return plugin type"""
    if not plugin_path.exists():
        raise FileNotFoundError(f"File '{plugin_path}' not found")

    if plugin_path.is_dir():
        return PluginType.DIR

    if is_tarfile(plugin_path):
        return PluginType.TAR

    if is_zipfile(plugin_path):
        return PluginType.ZIP

    raise TypeError("This program only supports tarball or zip files")


def check_plugin_structure(
    plugin_path: Path, plugin_type: PluginType
) -> PluginsDataList:
    """Check the minimum plugin structure (a directory with a plugin.py file)
    and return its name"""
    plugins_data_list = []
    exp_toml = "plugin.toml"
    exp_file = ""

    try:
        if PluginType.DIR == plugin_type:
            exp_file = exp_toml
            plugin_dict = load_toml(plugin_path / exp_file)["plugin"]
            exp_file = plugin_path / plugin_dict["start"]
            if not Path(exp_file).exists():
                raise FileNotFoundError()
            plugins_data_list.append(plugin_dict)

        elif PluginType.TAR == plugin_type:
            with tar_open(plugin_path) as f:
                # get the list of plugin.toml files
                exp_file = exp_toml
                tar_toml_list = [
                    item.name for item in f.getmembers() if exp_file in item.name
                ]
                if not tar_toml_list:
                    raise FileNotFoundError()

                # getmember and extractfile raise a KeyError if the file cannot be found
                for toml_file in tar_toml_list:
                    # Verify the toml file is in a directory
                    exp_file = f"DIRECTORY/{exp_toml}"
                    dir_name = toml_file.split("/")[0]
                    f.getmember(dir_name)

                    # Read the toml file and check that the file
                    # defined in "start" is present
                    with f.extractfile(toml_file) as file:  # type: ignore[union-attr]
                        plugin_dict = toml_loads(file.read().decode("utf-8"))["plugin"]
                        exp_file = f'{dir_name}/{plugin_dict["start"]}'
                        f.getmember(exp_file)
                        plugins_data_list.append(plugin_dict)

        elif PluginType.ZIP == plugin_type:
            with ZipFile(plugin_path) as f:
                # get the list of plugin.toml files
                exp_file = exp_toml
                zip_toml_list = [
                    item.filename for item in f.infolist() if exp_file in item.filename
                ]
                if not zip_toml_list:
                    raise FileNotFoundError()

                # getinfo and open raise a KeyError if the file cannot be found
                for toml_file in zip_toml_list:
                    # Verify the toml file is in a directory
                    exp_file = f"DIRECTORY/{exp_toml}"
                    dir_name = toml_file.split("/")[0]
                    f.getinfo(f"{dir_name}/")

                    # Read the toml file and check that the file
                    # defined in "start" is present
                    with f.open(toml_file) as file:
                        plugin_dict = toml_loads(file.read().decode("utf-8"))["plugin"]
                        exp_file = f'{dir_name}/{plugin_dict["start"]}'
                        f.getinfo(exp_file)
                        plugins_data_list.append(plugin_dict)

    except (FileNotFoundError, KeyError) as e:
        raise InvalidPluginError(
            f"File '{exp_file}' not found in '{plugin_path.name}'"
        ) from e

    return plugins_data_list


def move_plugin_data(
    plugin_name: str,
    plugin_path: Path,
    plugin_type: PluginType,
    dest_path: Path = PluginsConfig.ROOT_DIR,
) -> None:
    """Move the plugin data to ~/.hekit/plugins"""
    if PluginType.DIR == plugin_type:
        copytree(plugin_path, dest_path / plugin_name)
    elif PluginType.TAR == plugin_type:
        with tar_open(plugin_path) as f:
            tar_items = [item for item in f.getmembers() if plugin_name in item.name]
            f.extractall(dest_path, tar_items)
    elif PluginType.ZIP == plugin_type:
        with ZipFile(plugin_path) as f:
            zip_items = [item for item in f.infolist() if plugin_name in item.filename]
            f.extractall(dest_path, zip_items)


def install_plugin(args) -> None:
    """Install third party plugins"""
    config_dict = load_plugins_config_file()
    plugin_path = Path(args.plugin).resolve()
    plugin_type = get_plugin_type(plugin_path)
    plugins_data_list = check_plugin_structure(plugin_path, plugin_type)

    for plugin_dict in plugins_data_list:
        plugin_name = plugin_dict["name"]
        if args.force:
            # remove the present version
            rmtree(PluginsConfig.ROOT_DIR / plugin_name)
        elif plugin_name in config_dict.keys():
            # check the versions because the plugin is in the system
            plugin_version = plugin_dict["version"]
            config_version = config_dict[plugin_name]["version"]
            if config_version == plugin_version:
                print(
                    f"{plugin_name} version {plugin_version} is already installed in the system"
                )
                continue
            # Installing a different version
            user_answer = input(
                f"You are trying to install {plugin_name} version {plugin_version}.\n"
                f"However the version {config_version} was found in the system.\n"
                "Do you want to remove the present version and continue? (y/n) "
            )
            if user_answer in ("y", "Y"):
                continue
            # remove the present version
            rmtree(PluginsConfig.ROOT_DIR / plugin_name)

        move_plugin_data(plugin_name, plugin_path, plugin_type)
        config_dict[plugin_name] = {
            "version": plugin_dict["version"],
            "state": PluginState.ENABLE,
        }
        update_plugins_config_file(config_dict)
        print(f"Plugin {plugin_name} was installed successfully")


def remove_plugin(args) -> None:
    """Remove third party plugins"""
    config_dict = load_plugins_config_file()

    if args.all:
        # Remove all third party plugins
        user_answer = input(
            "All plugins will be deleted. Do you want to continue? (y/n) "
        )
        if user_answer not in ("y", "Y"):
            return

        for plugin_name in config_dict.keys():
            rmtree(PluginsConfig.ROOT_DIR / plugin_name)

        config_dict.clear()
        print("All plugins were uninstalled successfully")
    else:
        # Remove a specific third party plugins
        plugin_name = args.plugin
        if not plugin_name:
            raise ValueError("A plugin name should be specified as argument")

        if plugin_name not in config_dict.keys():
            print(f"Plugin {plugin_name} was not found in the system")
            return

        rmtree(PluginsConfig.ROOT_DIR / plugin_name)
        del config_dict[plugin_name]
        print(f"Plugin {plugin_name} was uninstalled successfully")

    update_plugins_config_file(config_dict)


def update_plugin_state(args) -> None:
    """Enable third party plugins"""
    config_dict = load_plugins_config_file()
    plugin_name = args.plugin
    plugin_state = args.state

    if plugin_name not in config_dict.keys():
        print(f"Plugin {plugin_name} was not found in the system")
        return

    if config_dict[plugin_name]["state"] == plugin_state:
        print(f"Plugin {plugin_name} is already {plugin_state} in the system")
        return

    config_dict[plugin_name]["state"] = plugin_state
    update_plugins_config_file(config_dict)
    print(f"Plugin {plugin_name} was {plugin_state} successfully")


def list_plugins(args) -> None:
    """Print the list of all plugins"""
    config_dict = load_plugins_config_file()
    state = args.state

    width_name = max(map(len, config_dict.keys()), default=0) + 3
    width_status = 10

    filtered_plugin_dict = (
        config_dict.items()
        if state == "all"
        else ((k, v) for k, v in config_dict.items() if state == v["state"])
    )

    print(
        f"{'PLUGIN':{width_name}} {'VERSION':{width_status}} {'STATE':{width_status}}"
    )
    for k, v in filtered_plugin_dict:
        print(
            f"{k:{width_name}} {v['version']:{width_status}} {v['state']:{width_status}}"
        )


def set_plugin_subparser(subparsers) -> None:
    """Create the parser for the 'plugin' command"""
    parser_plugin = subparsers.add_parser(
        "plugins", description="handle third party plugins"
    )
    subparsers_plugin = parser_plugin.add_subparsers(help="sub-command help")

    # list options
    parser_list = subparsers_plugin.add_parser(
        "list", description="print the list of all plugins"
    )
    parser_list.add_argument(
        "--state",
        default="all",
        choices=["all", PluginState.ENABLE, PluginState.DISABLE],
        help="filter the plugins by their state",
    )
    parser_list.set_defaults(fn=list_plugins)

    # install options
    parser_install = subparsers_plugin.add_parser(
        "install", description="install a new plugin"
    )
    parser_install.add_argument(
        "plugin",
        type=validate_input,
        help="File with the plugin",
    )
    parser_install.add_argument(
        "--force", action="store_true", help="forces the installation process"
    )
    parser_install.set_defaults(fn=install_plugin)

    # remove options
    parser_remove = subparsers_plugin.add_parser(
        "remove", description="remove a plugin"
    )
    parser_remove.add_argument(
        "plugin",
        type=validate_input,
        help="plugin name",
        nargs="?",
        default="",
    ).completer = plugins_enable_completer
    parser_remove.add_argument(
        "--all",
        action="store_true",
        help="Remove all plugins in the system",
    )
    parser_remove.set_defaults(fn=remove_plugin)

    # enable options
    parser_enable = subparsers_plugin.add_parser(
        "enable", description="enable a plugin"
    )
    parser_enable.add_argument(
        "plugin", type=validate_input, help="plugin name"
    ).completer = plugins_disable_completer
    parser_enable.set_defaults(fn=update_plugin_state, state=PluginState.ENABLE)

    # disable options
    parser_disable = subparsers_plugin.add_parser(
        "disable", description="disable a plugin"
    )
    parser_disable.add_argument(
        "plugin", type=validate_input, help="plugin name"
    ).completer = plugins_enable_completer
    parser_disable.set_defaults(fn=update_plugin_state, state=PluginState.DISABLE)
