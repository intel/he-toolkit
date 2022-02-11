# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
import os


def list_dirs(path: str):
    """Return list of directories in path."""
    try:
        _, dirs, _ = next(os.walk(path))
        return dirs
    except StopIteration:
        return []


def list_components(args):
    """List to stdout info on components."""
    repo_location = args.config.repo_location
    # At the mo, just lists installed.
    width = 10
    print(
        f"{'component':{width}} {'instance':{width}} {'fetch':{width}} {'build':{width}} {'install':{width}}"
    )

    for comp_name in sorted(list_dirs(repo_location)):
        comp_name_path = f"{repo_location}/{comp_name}"
        for comp_inst in sorted(list_dirs(comp_name_path)):
            try:
                info_filepath = f"{comp_name_path}/{comp_inst}/hekit.info"
                info_file = toml.load(info_filepath)
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{info_file['status']['fetch']:{width}}",
                    f"{info_file['status']['build']:{width}}",
                    f"{info_file['status']['install']:{width}}",
                )
            except FileNotFoundError:
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"'{info_filepath}' not found",
                )
            except KeyError as emsg:
                print(
                    f"{comp_name:{width}} {comp_inst:{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"{'unknown':{width}}",
                    f"key {emsg} not found",
                )
