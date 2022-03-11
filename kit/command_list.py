# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from toml import load
from os import walk


def list_dirs(path: str):
    """Return list of directories in path."""
    try:
        dirs = next(walk(path))[1]  # dirs in a list
        return sorted(dirs)
    except StopIteration:
        return []


def get_number_spaces():
    """ Define the number of spaces after the widest
    component and instance to separate the columns"""
    return 2


def get_repo_properties(repo_location: str):
    """ Return a dictionary with the structure of the repo
        and widths of the widest component and instance"""
    # Get the components
    comp_list = list_dirs(repo_location)

    repo_structure = {}
    max_width_inst = 0
    # Get the width of the widest component
    max_width_comp = len(max(comp_list, key=len, default=""))

    for comp_name in comp_list:
        # Get the instances
        comp_name_path = f"{repo_location}/{comp_name}"
        inst_list = list_dirs(comp_name_path)

        # Get the width of the widest instance
        width_inst = len(max(inst_list, key=len, default=""))
        if width_inst > max_width_inst:
            max_width_inst = width_inst

        # Fill the dict where key=comp_name, value=instances
        repo_structure[comp_name] = inst_list

    return (
        repo_structure,
        max_width_comp + get_number_spaces(),
        max_width_inst + get_number_spaces(),
    )


def list_components(args):
    """List to stdout info on components."""
    repo_location = args.config.repo_location
    width_status = 10
    repo_structure, width_comp, width_inst = get_repo_properties(repo_location)

    # Header
    print(
        f"{'component':{width_comp}} {'instance':{width_inst}} {'fetch':{width_status}} {'build':{width_status}} {'install':{width_status}}"
    )

    for comp_name, inst_list in repo_structure.items():
        for comp_inst in inst_list:
            try:
                info_filepath = f"{repo_location}/{comp_name}/{comp_inst}/hekit.info"
                info_file = load(info_filepath)
                print(
                    f"{comp_name:{width_comp}} {comp_inst:{width_inst}}",
                    f"{info_file['status']['fetch']:{width_status}}",
                    f"{info_file['status']['build']:{width_status}}",
                    f"{info_file['status']['install']:{width_status}}",
                )
            except FileNotFoundError:
                print(
                    f"{comp_name:{width_comp}} {comp_inst:{width_inst}}",
                    f"{'unknown':{width_status}}",
                    f"{'unknown':{width_status}}",
                    f"{'unknown':{width_status}}",
                    f"'{info_filepath}' not found",
                )
            except KeyError as emsg:
                print(
                    f"{comp_name:{width_comp}} {comp_inst:{width_inst}}",
                    f"{'unknown':{width_status}}",
                    f"{'unknown':{width_status}}",
                    f"{'unknown':{width_status}}",
                    f"key {emsg} not found",
                )
