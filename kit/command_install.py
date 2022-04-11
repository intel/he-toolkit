# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from component_builder import components_to_build_from, chain_run


def _stages(upto_stage: str):
    """Return a generator"""
    if upto_stage not in ("fetch", "build", "install"):
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
    components = components_to_build_from(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )

    the_stages = _stages(args.upto_stage)

    for component in components:
        comp_label = f"{component.component_name()}/{component.instance_name()}"
        print(comp_label)
        if component.skip():
            print("Skipping", comp_label)
            continue

        chain_run(the_stages(component))


def get_recipe_arg_dict(recipe_arg: str):
    """Returns a dictionary filled with recipe_arg values"""
    recipe_arg_dict = {}

    for pair in recipe_arg.replace(" ", "").split(","):
        key_value = pair.split("=")

        if len(key_value) != 2:
            raise ValueError(f"Wrong format for {key_value}. Expected key=value")

        key, value = key_value
        recipe_arg_dict[key] = value

    return recipe_arg_dict


def set_install_subparser(subparsers):
    """create the parser for the 'install' command"""
    list = ["install", "build", "fetch"]

    for action in list:
        parser = subparsers.add_parser(action, description=f"{action} components")
        parser.add_argument(
            "recipe_file",
            metavar="recipe-file",
            type=str,
            help=f"TOML file for {action}",
        )
        parser.add_argument(
            "--recipe_arg",
            default={},
            type=get_recipe_arg_dict,
            help="Collection of key=value pairs separated by commas. The content of the TOML file will be replaced with this data.",
        )
        parser.set_defaults(fn=install_components, upto_stage=action)
