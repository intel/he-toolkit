#! /usr/bin/python3

import re
import toml
import sys
import argparse
from subprocess import Popen, PIPE, STDOUT

import pprint
from component_builder import ComponentBuilder, chain_run


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
    with Popen(cmd_and_args, stdout=PIPE, stderr=STDOUT) as proc:
        for line in proc.stdout:
            print(line.decode("ascii"), end="")
    return proc.returncode


def components_to_build_from(filename, label):
    """Returns a generator that yields a component to be built and/or installed"""
    toml_dict = toml.load(filename)
    label_objs = toml_dict[label]
    return (ComponentBuilder(obj) for obj in label_objs)


def install_components(args):
    """"""

    label = "dependencies"
    components = components_to_build_from(args.install_file, label)

    for component in components:
        print(label)
        chain_run(
            [
                component.pre_build,
                component.build,
                component.post_build,
                component.install,
            ]
        )


def list_installed_components(args):
    """"""


def remove_components(args):
    """"""


def parse_cmds():
    """"""
    # create the top-level parser
    parser = argparse.ArgumentParser(prog="PROG")
    #    parser.add_argument('--foo', action='store_true', help='foo help')
    subparsers = parser.add_subparsers(help="sub-command help")

    # create the parser for the "list" command
    parser_list = subparsers.add_parser("list", help="lists installed components")
    #    parser_list.add_argument('bar', type=int, help='bar help')
    parser_list.set_defaults(fn=list_installed_components)

    # create the parser for the "install" command
    parser_install = subparsers.add_parser("install", help="installs components")
    parser_install.add_argument(
        "install_file",
        metavar="install-file",
        type=str,
        help="TOML file for installations",
    )
    parser_install.set_defaults(fn=install_components)

    # create the parser for the "remove" command
    parser_remove = subparsers.add_parser(
        "remove", help="removes/uninstalls components"
    )
    #    parser_remove.add_argument('--baz', choices='XYZ', help='baz help')
    parser_remove.set_defaults(fn=remove_components)

    return parser.parse_args()


def main():
    # Parse cmdline
    args = parse_cmds()

    # Run the command
    args.fn(args)

    print(args)


if __name__ == "__main__":
    main()
