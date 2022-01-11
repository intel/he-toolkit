# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
from component_builder import ComponentBuilder, chain_run


def components_to_build_from(filename, repo_location):
    """Returns a generator that yields a component to be built and/or installed"""
    components = toml.load(filename)
    # Extracting specs also flattens 'list of list' to list
    specs = ((name, spec) for name, specs in components.items() for spec in specs)

    return (ComponentBuilder(name, spec, repo_location) for name, spec in specs)


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
