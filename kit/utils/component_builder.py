# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module executes the actions specified by the user in the hekit arguments"""

import shlex
from os import chdir as change_directory_to
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT  # nosec B404
from typing import Iterable, Callable

from kit.utils.files import dump_toml, load_toml
from kit.utils.spec import Spec

RunOutput = tuple[bool, int]


def install_components_from_recipe_file(
    recipe_file: str, upto_stage: str, repo_location: str, force: bool, recipe_args
) -> None:
    """install components from a recipe file upto a given stage"""
    if Path(recipe_file).is_symlink():
        raise TypeError("The TOML file cannot be a symlink")

    the_stages = stages(upto_stage, force)

    components = components_to_build_from(recipe_file, repo_location, recipe_args)

    for component in components:
        chain_run(the_stages(component))


def hekit_print(*args, box_msg="HEKIT", **kwargs) -> None:
    """print but prefixes [HEKIT] or other if box_msg given"""
    args_prefixed = [arg.replace("\n", f"\n[{box_msg}]") for arg in map(str, args)]
    print(f"[{box_msg}]", *args_prefixed, **kwargs)


def stages(upto_stage: str, force: bool) -> Callable:
    """Return a generator function that handles a component"""
    if upto_stage not in ("fetch", "build", "install"):
        raise ValueError(f"Not a valid stage value '{upto_stage}'")

    def the_stages(component):
        comp_label = f"{component.component_name()}/{component.instance_name()}"
        hekit_print("component/instance:", comp_label)
        if component.skip():
            hekit_print("Skipping component/instance:", comp_label)
            return

        # upto_stage is re-executed only when "force" flag is set.
        # if previous stages were executed successfully, they are going to be skipped.
        # For example, fetch and build could be skipped when executing install.
        if force:
            component.reset_stage_info_file(upto_stage)

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


class BuildError(Exception):
    """Exception for something wrong with the build."""

    def __init__(self, message: str, error: int) -> None:
        super().__init__(message)
        self.error = error


def chain_run(funcs: Iterable[Callable]):
    """Run functions sequentially. Fail at first function with failed
    return value."""
    for fn in funcs:
        success, return_code = fn()
        if not success:
            raise BuildError(
                f"Function '{fn.__name__}' failed to execute external process",
                return_code,
            )


def run(cmd_and_args: str | list[str]) -> RunOutput:
    """Takes either a string or list of strings and runs as command."""
    if not cmd_and_args:
        return True, 0

    if isinstance(cmd_and_args, str):
        cmd_and_args_list = shlex.split(cmd_and_args)
        hekit_print(cmd_and_args)
    else:
        cmd_and_args_list = cmd_and_args
        hekit_print(" ".join(cmd_and_args))
    basename = Path(cmd_and_args_list[0]).name.upper()  # Capitalized
    with Popen(cmd_and_args_list, stdout=PIPE, stderr=STDOUT) as proc:  # nosec B603
        if proc.stdout is None:
            raise ValueError("STDOUT is None")
        for line in proc.stdout:
            hekit_print(line.decode("utf-8").rstrip(), box_msg=basename)
    success = proc.returncode == 0
    return success, proc.returncode


def components_to_build_from(
    filename: str, repo_location: str, recipe_arg_dict: dict[str, str]
):
    """Returns a generator that yields a component to be built and/or installed"""
    specs = Spec.from_toml_file(filename, repo_location, recipe_arg_dict)
    return (ComponentBuilder(spec) for spec in specs)


class ComponentBuilder:
    """Objects of this class can orchestrate the build of a component"""

    def __init__(self, spec: Spec) -> None:
        """Initialize a ComponentBuilder from a Spec object"""
        if not isinstance(spec, Spec):
            raise TypeError(
                f"A spec must be type Spec, but got '{type(spec).__name__}'"
            )

        self._spec = spec
        self._location = f"{spec.repo_location}/{spec.component}/{spec.name}"

        # load previous from info file
        try:
            self._info_file = load_toml(f"{self._location}/hekit.info")
        except FileNotFoundError:
            self._info_file = {"status": {"fetch": "", "build": "", "install": ""}}

    def skip(self) -> bool:
        """Returns skip value"""
        return self._spec.skip

    def _try_run(self, attrib: str) -> RunOutput:
        """Try to run the attrib in the spec.
        Do nothing (pass success) if no key in dict.
        """
        hekit_print(attrib)
        try:
            return run(self._spec[attrib])
        except KeyError:
            return True, 0

    def component_name(self) -> str:
        """Returns component name"""
        return self._spec.component

    def instance_name(self) -> str:
        """Returns instance name"""
        return self._spec.name

    def setup(self) -> RunOutput:
        """Create the layout for the component"""
        root = Path(self._location)
        for dirname in ("fetch", "build", "install"):
            (root / dirname).mkdir(exist_ok=True, parents=True)

        # Save expanded copy on disk
        self._spec.to_toml_file(root / "hekit.spec")

        # Should return successful
        return True, 0

    def already_successful(self, stage: str) -> bool:
        """Returns True if stage already recorded in info file
        as successful"""
        return self._info_file["status"][stage] == "success"

    def update_info_file(self, stage: str, success: bool) -> None:
        """Updates the hekit.info file"""
        self._info_file["status"][stage] = "success" if success else "failure"
        dump_toml(f"{self._location}/hekit.info", self._info_file)

    def reset_stage_info_file(self, stage):
        """Reset the stage value that was read from hekit.info file"""
        self._info_file["status"][stage] = ""

    def _stage(self, stage: str) -> RunOutput:
        hekit_print(stage)
        if self.already_successful(stage):
            return True, 0

        def closure():
            return run(self._spec[stage])

        fns = [getattr(self, f"pre_{stage}"), closure, getattr(self, f"post_{stage}")]

        # The actual directory that is written to
        init_stage_dir = self._spec[f"init_{stage}_dir"]
        change_directory_to(Path(init_stage_dir).expanduser())
        hekit_print("current directory:", Path.cwd())

        try:
            chain_run(fns)
            self.update_info_file(stage, success=True)
            return True, 0
        except BuildError as e:
            self.update_info_file(stage, success=False)
            return False, e.error

    def pre_fetch(self) -> RunOutput:
        """Any steps after a fetch"""
        return self._try_run("pre-fetch")

    def fetch(self) -> RunOutput:
        """Fetch the source"""
        return self._stage("fetch")

    def post_fetch(self) -> RunOutput:
        """Any steps after a fetch"""
        return self._try_run("post-fetch")

    def pre_build(self) -> RunOutput:
        """Any setup steps before building"""
        return self._try_run("pre-build")

    def build(self) -> RunOutput:
        """Build the software"""
        return self._stage("build")

    def post_build(self) -> RunOutput:
        """Any steps after a build"""
        return self._try_run("post-build")

    def pre_install(self) -> RunOutput:
        """Any steps before an install"""
        return self._try_run("pre-install")

    def install(self) -> RunOutput:
        """Installation of the component, ready to use"""
        return self._stage("install")

    def post_install(self) -> RunOutput:
        """Any steps after an install"""
        return self._try_run("post-install")
