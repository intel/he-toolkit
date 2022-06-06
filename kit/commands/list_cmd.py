# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module lists the libraries that were installed with hekit"""

from os import walk
from pathlib import Path
from itertools import chain
from typing import Dict, List

from toml import load

# Number of separation spaces for columns
_SEP_SPACES = 2


class RepoProperties:
    """ Contains a dictionary with the structure of the repo
        and widths of the widest component and instance"""

    def __init__(self, repo_location: str, separation_spaces: int = _SEP_SPACES):
        # Get the components and instances
        self._repo_structure = RepoProperties._repo_struct(repo_location)

        # Get the width of the widest component
        self.width_comp = self.max_len(self._repo_structure.keys())

        # Get the width of the widest instance
        all_instances = self._repo_structure.values()
        self.width_inst = self.max_len(chain.from_iterable(all_instances))

        # Include column separation
        self.width_comp += separation_spaces
        self.width_inst += separation_spaces
        self.width_status = 10
        self.separation_spaces = separation_spaces

    def max_len(self, iterable):
        """Return the width of the widest string"""
        return max(map(len, iterable), default=0)

    @property
    def structure(self) -> Dict[str, List[str]]:
        """Return a dictionary with the structure of the repo"""
        return self._repo_structure

    @staticmethod
    def _repo_struct(path: str) -> Dict[str, List[str]]:
        """Return a dictionary with sorted keys as components and values as
           sorted list of instances"""
        path = Path(path)
        return {component: list_dirs(path / component) for component in list_dirs(path)}


# TODO move out into some util module
# This is a util func also used for tab completion
def list_dirs(path: str) -> List[str]:
    """Return list of directories in path."""
    try:
        dirs = next(walk(path))[1]  # dirs in a list
        return sorted(dirs)
    except StopIteration:
        return []


def list_components(args):
    """List to stdout info on components."""
    repo_location = Path(args.config.repo_location)
    repo_properties = RepoProperties(repo_location)

    # Aliases
    width_status = repo_properties.width_status
    width_comp = repo_properties.width_comp
    width_inst = repo_properties.width_inst

    # Header
    print(
        f"{'COMPONENT':{width_comp}} {'INSTANCE':{width_inst}} {'FETCH':{width_status}} {'BUILD':{width_status}} {'INSTALL':{width_status}}"
    )

    for comp_name, inst_list in repo_properties.structure.items():
        for comp_inst in inst_list:
            try:
                info_filepath = repo_location / comp_name / comp_inst / "hekit.info"
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
                    f"file '{info_filepath}' not found",
                )
            except KeyError as emsg:
                print(
                    f"{comp_name:{width_comp}} {comp_inst:{width_inst}}",
                    f"{'unknown':{width_status}}",
                    f"{'unknown':{width_status}}",
                    f"{'unknown':{width_status}}",
                    f"key {emsg} not found",
                )


def set_list_subparser(subparsers):
    """create the parser for the 'list' command"""
    parser_list = subparsers.add_parser(
        "list", description="lists installed components"
    )
    parser_list.set_defaults(fn=list_components)
