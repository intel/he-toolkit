# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from component_builder import components_to_build_from, chain_run


def _stages(upto_stage: str):
    """Return a generator"""
    if upto_stage not in ("fetch, build, install"):
        raise ValueError(f"Not a valid stage value '{upto_stage}'")

    def the_stages(component):
        yield component.setup
        yield component.fetch
        if upto_stage == "fetch":
            return
        yield component.build
        if upto_stage == "build":
            return
        yield component.install
        return

    return the_stages


def install_components(args):
    """Install command"""
    repo_location = args.config.repo_location
    components = components_to_build_from(args.recipe_file, repo_location)

    the_stages = _stages(args.upto_stage)

    for component in components:
        comp_label = f"{component.component_name()}/{component.instance_name()}"
        print(comp_label)
        if component.skip():
            print(f"Skipping", comp_label)
            continue
        chain = [component.setup, component.fetch, component.build, component.install]
        chain_run(the_stages(component))
