# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from shutil import rmtree


def remove_components(args):
    """Remove component instances"""
    repo_location = args.config.repo_location
    try:
        component = args.component
        instance = args.instance
        path = f"{repo_location}/{component}/{instance}"
        rmtree(path)
        print(f"Instance '{instance}' of component '{component}' successfully removed")

    except FileNotFoundError:
        print(
            "Nothing to remove",
            f"Instance '{instance}' of component '{component}' not found.",
        )
