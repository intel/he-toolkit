#! /usr/bin/python3

import toml
import sys
import argparse
from subprocess import Popen, PIPE, STDOUT

import pprint

def run(cmd_and_args):
    with Popen(cmd_and_args, stdout=PIPE, stderr=STDOUT) as proc:
        for line in proc.stdout:
            print(line.decode("ascii"), end="")
    return proc.returncode


# run(["ls", "-al", "wow"])

def install_components(args):
    """"""
    pp = pprint.PrettyPrinter(indent=4)
    t = toml.load(args.install_file)
    pp.pprint(t)

# components = components_to_build_from(toml_file)
# for component in components:
#     print(component.label())
#     success, return_code = component.install()
#     if success:
#         print(success)
#     else:
#         print(success, return_code)



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
    parser_remove = subparsers.add_parser("remove", help="removes/uninstalls components")
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
