# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from component_builder import components_to_build_from, chain_run


def install_components(args):
    """Install command"""
    repo_location = args.config.repo_location
    components = components_to_build_from(args.install_file, repo_location)

    for component in components:
        comp_label = f"{component.component_name()}/{component.instance_name()}"
        print(comp_label)
        if component.skip():
            print(f"Skipping", comp_label)
            continue
        chain_run(
            [component.setup, component.fetch, component.build, component.install]
        )
