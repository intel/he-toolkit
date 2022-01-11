# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import re
import toml
import shlex
import os
from subprocess import Popen, PIPE, STDOUT


def read_spec(component, name, attrib, repo_location):
    """Return spec file as a dict"""
    path = f"{repo_location}/{component}/{name}/hekit.spec"
    spec = toml.load(path)
    return spec[attrib]


class BuildError(Exception):
    """Exception for something wrong with the build."""

    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


def chain_run(funcs):
    """Run functions sequentially. Fail at first function with failed
       return value."""
    for fn in funcs:
        success, return_code = fn()
        if not success:
            raise BuildError(
                f"Function '{fn.__name__}' failed to execute external process",
                return_code,
            )


def fill_self_ref_string_dict(d, repo_path):
    """Returns a dict with str values.
    NB. Only works for flat str value dict."""

    def fill_str(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = re.findall(r"(%(.*?)%)", s)
            if not symbols:
                return s

            new_s = s
            for symbol, k in symbols:
                new_s = new_s.replace(symbol, fill_str(d[k]))

            return new_s
        elif isinstance(s, list):
            return [fill_str(e) for e in s]
        else:
            # Not str or list
            return s

    def fill_dep_str(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = re.findall(r"(\$(.*?)/(.*?)/(.*?)\$)", s)
            if not symbols:
                return s

            new_s = s
            for symbol, comp, name, k in symbols:
                # Assume finalised spec is already expanded
                sub = read_spec(comp, name, k, repo_path)
                new_s = new_s.replace(symbol, sub)

            return new_s
        elif isinstance(s, list):
            return [fill_dep_str(e) for e in s]
        else:
            # Not str or list
            return s

    return {k: fill_dep_str(fill_str(v)) for k, v in d.items()}


def run(cmd_and_args):
    """Takes either a string or list of strings and runs as command."""
    if not cmd_and_args:
        return True, 0

    if isinstance(cmd_and_args, str):
        cmd_and_args_list = shlex.split(cmd_and_args)
        print(cmd_and_args)
    else:
        cmd_and_args_list = cmd_and_args
        print(" ".join(cmd_and_args))
    basename = os.path.basename(cmd_and_args_list[0]).upper()  # Capitalized
    with Popen(cmd_and_args_list, stdout=PIPE, stderr=STDOUT) as proc:
        for line in proc.stdout:
            print(f"[{basename}]", line.decode("utf-8"), end="")
    success = True if proc.returncode == 0 else False
    return success, proc.returncode


def try_run(spec: dict, attrib: str):
    """Try to run the attrib in the spec.
       Do nothing (pass success) if no key in dict.
    """
    try:
        return run(spec[attrib])
    except KeyError:
        return True, 0


def change_cwd_to(path):
    expanded_path = os.path.expanduser(path)
    os.chdir(expanded_path)
    print("cwd:", expanded_path)


def fill_init_paths(d, repo_location):
    """Create absolute path for the top-level attribs that begin
       with 'init_' by prepending repo location"""
    for k, v in d.items():
        if k.startswith("init_") or k.startswith("export_"):
            d[k] = f"{repo_location}/{v}"
    return d


class ComponentBuilder:
    """Objects of this class can orchestrate the build of a component"""

    def __init__(self, comp_name, spec, repo_path):
        """"""
        if not isinstance(spec, dict):
            raise TypeError(
                f"A spec must be type dict, but got '{type(spec).__name__}'"
            )
        self._repo_path = repo_path
        # FIXME .regression. convoluted code means name cannot be currently back substituted
        self._comp_instance = spec["name"]
        self._comp_name = comp_name
        self._location = f"{repo_path}/{comp_name}/{self._comp_instance}"
        self._skip = spec["skip"] if "skip" in spec else False
        # FIXME This logic is convoluted. Must update self._spec
        self._spec = fill_init_paths(spec, self._location)
        self._spec = fill_self_ref_string_dict(self._spec, repo_path)

        if not isinstance(self._skip, bool):
            raise ValueError("Skip must be set to true or false")

        # load previous from info file
        try:
            with open(f"{self._location}/hekit.info") as info_file:
                self._info_file = toml.load(info_file)
        except FileNotFoundError:
            self._info_file = {"status": {"fetch": "", "build": "", "install": ""}}

    def skip(self):
        return self._skip

    def component_name(self):
        return self._comp_name

    def instance_name(self):
        return self._comp_instance

    def setup(self):
        """Create the layout for the component"""
        root = self._location
        for dirname in ("fetch", "build", "install"):
            try:
                os.makedirs(f"{root}/{dirname}")
            except FileExistsError:
                pass  # nothing to do

        # Save expanded copy on disk
        with open(f"{root}/hekit.spec", "w") as f:
            toml.dump(self._spec, f)

        # Should return successful
        return True, 0

    def already_successful(self, stage):
        """Returns True if stage already recorded in info file
           as successul"""
        return self._info_file["status"][stage] == "success"

    def update_info_file(self, stage, success):
        with open(f"{self._location}/hekit.info", "w") as info_file:
            self._info_file["status"][stage] = "success" if success else "failure"
            toml.dump(self._info_file, info_file)

    def _stage(self, stage):
        print(stage)
        if self.already_successful(stage):
            return True, 0

        def closure():
            return run(self._spec[stage])

        fns = []
        # Will need run add a pre_method if it exists
        if f"pre_{stage}" in dir(self):
            fns.append(getattr(self, f"pre_{stage}"))

        # Now run the stage
        fns.append(closure)

        # And same again for post_method if it exists
        if f"post_{stage}" in dir(self):
            fns.append(getattr(self, f"post_{stage}"))

        # The actual directory that is written to
        init_stage_dir = self._spec[f"init_{stage}_dir"]
        change_cwd_to(init_stage_dir)

        try:
            chain_run(fns)
            self.update_info_file(stage, success=True)
            return True, 0
        except BuildError as be:
            self.update_info_file(stage, success=False)
            return False, be.error

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

    def install(self):
        """Installation of the component, ready to use"""
        return self._stage("install")
