# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import re
import toml
import shlex
import os
from subprocess import Popen, PIPE, STDOUT


class BuildError(Exception):
    """Exception for something wrong with the build."""

    def __init__(self, message):
        super().__init__(message)


def chain_run(funcs):
    """"""
    for fn in funcs:
        success, return_code = fn()
        if success:
            print("success")
        else:
            print("failure", return_code)
            raise BuildError("")


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
    if isinstance(cmd_and_args, str):
        cmd_and_args_list = shlex.split(cmd_and_args)
        print(cmd_and_args)
    else:
        cmd_and_args_list = cmd_and_args
        print(" ".join(cmd_and_args))

    basename = os.path.basename(cmd_and_args_list[0]).upper()  # Capitalized
    with Popen(cmd_and_args_list, stdout=PIPE, stderr=STDOUT) as proc:
        for line in proc.stdout:
            print(f"[{basename}]", line.decode("ascii"), end="")
    success = True if proc.returncode == 0 else False
    return success, proc.returncode


def change_cwd_to(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    os.chdir(path)


class ComponentBuilder:
    def __init__(self, category, comp_name, spec, repo_path):
        """"""
        if not isinstance(spec, dict):
            raise TypeError(
                f"A spec must be type dict, but got '{type(spec).__name__}'"
            )
        self.__spec = fill_self_ref_string_dict(spec)
        self.__comp_instance = self.__spec["name"]
        self.__location = f"{repo_path}/{comp_name}/{self.__comp_instance}"
        self.__skip = self.__spec["skip"] if "skip" in self.__spec else False
        if not isinstance(self.__skip, bool):
            raise ValueError("Skip must be set to true or false")
        print(self.__spec)

        # load previous from info file
        try:
            with open(f"{self.__location}/hekit.info") as info_file:
                self.__info_file = toml.load(info_file)
        except FileNotFoundError:
            self.__info_file = {
                "status": {"fetch": None, "build": None, "install": None}
            }

    def skip(self):
        return self.__skip

    def setup(self):
        root = self.__location
        for dirname in ("fetch", "build", "install"):
            try:
                os.makedirs(f"{root}/{dirname}")
            except FileExistsError:
                pass  # nothing to do
        # Should return successful
        return True, 0

    def already_successful(self, stage):
        """Returns True if stage already recorded in info file
           as succcessul"""
        return self.__info_file["status"][stage] == "success"

    def update_info_file(self, stage, success):
        with open(f"{self.__location}/hekit.info", "w") as info_file:
            self.__info_file["status"][stage] = "success" if success else "failure"
            toml.dump(self.__info_file, info_file)

    def __stage(self, stage):
        print(stage)
        if self.already_successful(stage):
            return True, 0

        change_cwd_to(f"{self.__location}/{stage}")
        success, rt = run(self.__spec[stage])
        self.update_info_file(stage, success)
        return success, rt

    def fetch(self):
        """"""
        return self.__stage("fetch")

    def pre_build(self):
        """"""
        print("pre-build")
        success, rt = run(self.__spec["pre-build"])
        return success, rt

    def build(self):
        """"""
        return self.__stage("build")

    def post_build(self):
        """"""
        print("post-build")
        return True, 0

    def install(self):
        """"""
        return self.__stage("install")
