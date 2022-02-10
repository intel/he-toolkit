# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from component_builder import components_to_build_from, chain_run


def install_components(args):
    """Install command"""
    repo_location = args.config.repo_location
    components = components_to_build_from(args.recipe_file, repo_location)

    if args.upto_stage == "install":
        upto = 4
    elif args.upto_stage == "build":
        upto = 3
    elif args.upto_stage == "fetch":
        upto = 2
    else:
        raise ValueError(f"Not a valid stage value '{args.upto_stage}'")

    for component in components:
        comp_label = f"{component.component_name()}/{component.instance_name()}"
        print(comp_label)
        if component.skip():
            print(f"Skipping", comp_label)
            continue
        chain = [component.setup, component.fetch, component.build, component.install]
        chain_run(chain[:upto])
