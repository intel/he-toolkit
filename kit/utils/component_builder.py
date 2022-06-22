# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module executes the actions specified by the user in the hekit arguments"""

import shlex
from os import chdir as change_directory_to
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from typing import Iterable, Callable, Union, List
from typing import Dict
import toml
from utils.spec import Spec


class BuildError(Exception):
    """Exception for something wrong with the build."""

    def __init__(self, message, error):
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


def run(cmd_and_args: Union[str, List[str]]):
    """Takes either a string or list of strings and runs as command."""
    if not cmd_and_args:
        return True, 0

    if isinstance(cmd_and_args, str):
        cmd_and_args_list = shlex.split(cmd_and_args)
        print(cmd_and_args)
    else:
        cmd_and_args_list = cmd_and_args
        print(" ".join(cmd_and_args))
    basename = Path(cmd_and_args_list[0]).name.upper()  # Capitalized
    with Popen(cmd_and_args_list, stdout=PIPE, stderr=STDOUT) as proc:
        for line in proc.stdout:
            print(f"[{basename}]", line.decode("utf-8"), end="")
    success = proc.returncode == 0
    return success, proc.returncode


def try_run(spec: dict, attrib: str):
    """Try to run the attrib in the spec.
       Do nothing (pass success) if no key in dict.
    """
    try:
        return run(spec[attrib])
    except KeyError:
        return True, 0


def components_to_build_from(
    filename: str, repo_location: str, recipe_arg_dict: Dict[str, str]
):
    """Returns a generator that yields a component to be built and/or installed"""
    specs = Spec.from_toml_file(filename, repo_location, recipe_arg_dict)
    return (ComponentBuilder(spec) for spec in specs)


class ComponentBuilder:
    """Objects of this class can orchestrate the build of a component"""

    def __init__(self, spec: Spec):
        """Initialize a ComponentBuilder from a Spec object"""
        if not isinstance(spec, Spec):
            raise TypeError(
                f"A spec must be type Spec, but got '{type(spec).__name__}'"
            )

        self._spec = spec
        self._location = f"{spec.repo_location}/{spec.component}/{spec.name}"

        # load previous from info file
        try:
            with open(f"{self._location}/hekit.info", encoding="utf-8") as info_file:
                self._info_file = toml.load(info_file)
        except FileNotFoundError:
            self._info_file = {"status": {"fetch": "", "build": "", "install": ""}}

    def skip(self):
        """Returns skip value"""
        return self._spec.skip

    def component_name(self):
        """Returns component name"""
        return self._spec.component

    def instance_name(self):
        """Returns instance name"""
        return self._spec.name

    def setup(self):
        """Create the layout for the component"""
        root = Path(self._location)
        for dirname in ("fetch", "build", "install"):
            (root / dirname).mkdir(exist_ok=True, parents=True)

        # Save expanded copy on disk
        self._spec.to_toml_file(root / "hekit.spec")

        # Should return successful
        return True, 0

    def already_successful(self, stage):
        """Returns True if stage already recorded in info file
           as successful"""
        return self._info_file["status"][stage] == "success"

    def update_info_file(self, stage, success):
        """Updates the hekit.info file"""
        with open(f"{self._location}/hekit.info", "w", encoding="utf-8") as info_file:
            self._info_file["status"][stage] = "success" if success else "failure"
            toml.dump(self._info_file, info_file)

    def reset_stage_info_file(self, stage):
        """Reset the stage value that was read from hekit.info file"""
        self._info_file["status"][stage] = ""

    def _stage(self, stage: str):
        print(stage)
        if self.already_successful(stage):
            return True, 0

        def closure():
            return run(self._spec[stage])

        fns = [getattr(self, f"pre_{stage}"), closure, getattr(self, f"post_{stage}")]

        # The actual directory that is written to
        init_stage_dir = self._spec[f"init_{stage}_dir"]
        change_directory_to(Path(init_stage_dir).expanduser())
        print("cwd:", Path.cwd())

        try:
            chain_run(fns)
            self.update_info_file(stage, success=True)
            return True, 0
        except BuildError as e:
            self.update_info_file(stage, success=False)
            return False, e.error

    def pre_fetch(self):
        """Any steps after a fetch"""
        print("pre-fetch")
        return try_run(self._spec, "pre-fetch")

    def fetch(self):
        """Fetch the source"""
        return self._stage("fetch")

    def post_fetch(self):
        """Any steps after a fetch"""
        print("post-fetch")
        return try_run(self._spec, "post-fetch")

    def pre_build(self):
        """Any setup steps before building"""
        print("pre-build")
        return try_run(self._spec, "pre-build")

    def build(self):
        """Build the software"""
        return self._stage("build")

    def post_build(self):
        """Any steps after a build"""
        print("post-build")
        return try_run(self._spec, "post-build")

    def pre_install(self):
        """Any steps after a install"""
        print("pre-install")
        return try_run(self._spec, "pre-install")

    def install(self):
        """Installation of the component, ready to use"""
        return self._stage("install")

    def post_install(self):
        """Any steps after a install"""
        print("post-install")
        return try_run(self._spec, "post-install")
