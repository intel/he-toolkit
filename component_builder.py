# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import re
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
            raise TypeError(
                f"fill_str expects type str, but got type '{type(s).__name__}'"
            )

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
    cmd_and_args_list = (
        shlex.split(cmd_and_args) if isinstance(cmd_and_args, str) else cmd_and_args
    )
    basename = os.path.basename(cmd_and_args_list[0]).upper()  # Capitalized
    with Popen(cmd_and_args_list, stdout=PIPE, stderr=STDOUT) as proc:
        for line in proc.stdout:
            print(f"[{basename}]", line.decode("ascii"), end="")
    success = True if proc.returncode == 0 else False
    return success, proc.returncode


class ComponentBuilder:
    def __init__(self, spec):
        """"""
        if not isinstance(spec, dict):
            raise TypeError(
                f"A spec must be type dict, but got '{type(spec).__name__}'"
            )
        os.chdir("tmp")
        print("Working in:", os.getcwd())
        self.__spec = fill_self_ref_string_dict(spec)
        print(self.__spec)

    def fetch(self):
        """"""
        print("fetch")
        success, rt = run(self.__spec["fetch"])
        return success, rt

    def pre_build(self):
        """"""
        print("pre-build")
        # rt = run(self.spec)
        return True, 0

    def build(self):
        """"""
        print("build")
        return True, 0

    def post_build(self):
        """"""
        print("post-build")
        return True, 0

    def install(self):
        """"""
        print("install")
        return True, 0
