# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import re
import toml
import shlex
import os
from subprocess import Popen, PIPE, STDOUT


class BuildError(Exception):
    """Exception for something wrong with the build."""

    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


def chain_run(funcs):
    """"""
    for fn in funcs:
        success, return_code = fn()
        if not success:
            raise BuildError(
                f"Function '{fn.__name__}' failed to execute external process",
                return_code,
            )


def fill_self_ref_string_dict(d):
    """Returns a dict with str values.
    NB. Only works for flat str value dict."""

    def fill_str(s):
        if not isinstance(s, str):
            # Not string do nothing
            return s

        symbols = re.findall(r"(%(.*?)%)", s)
        if not symbols:
            return s

        new_s = s
        for symbol, k in symbols:
            new_s = new_s.replace(symbol, fill_str(d[k]))

        return new_s

    return {k: fill_str(v) for k, v in d.items()}


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


def change_cwd_to(path):
    expanded_path = os.path.expanduser(path)
    os.chdir(expanded_path)


class ComponentBuilder:
    def __init__(self, category, comp_name, spec, repo_path):
        """"""
        if not isinstance(spec, dict):
            raise TypeError(
                f"A spec must be type dict, but got '{type(spec).__name__}'"
            )
        self._spec = fill_self_ref_string_dict(spec)
        self._comp_instance = self._spec["name"]
        self._location = f"{repo_path}/{comp_name}/{self._comp_instance}"
        self._skip = self._spec["skip"] if "skip" in self._spec else False
        if not isinstance(self._skip, bool):
            raise ValueError("Skip must be set to true or false")
        print(self._spec)

        # load previous from info file
        try:
            with open(f"{self._location}/hekit.info") as info_file:
                self._info_file = toml.load(info_file)
        except FileNotFoundError:
            self._info_file = {"status": {"fetch": "", "build": "", "install": ""}}

    def skip(self):
        return self._skip

    def setup(self):
        """Create the layout for the component"""
        root = self._location
        for dirname in ("fetch", "build", "install"):
            try:
                os.makedirs(f"{root}/{dirname}")
            except FileExistsError:
                pass  # nothing to do
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

        stage_dir = self._spec[f"{stage}_dir"]
        change_cwd_to(stage_dir)

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

    def pre_build(self):
        """Any setup steps before building"""
        print("pre-build")
        return run(self._spec["pre-build"])

    def build(self):
        """Build the software"""
        return self._stage("build")

    def post_build(self):
        """Any steps after a build"""
        print("post-build")
        return run(self._spec["post-build"])

    def install(self):
        """Installation of the component, ready to use"""
        return self._stage("install")
