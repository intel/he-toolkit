import os.path
from os import path

from openfhe.configurator import Configurator


def set_openfhe_subparser(subparsers):
    parser = subparsers.add_parser("openfhe", description="OpenFHE configurator WIP")
    parser.add_argument(
        "--del",
        type=bool,
        default=True,
        action="store_true",
        help="If a previous staging directory exists, delete.",
    )
    parser.add_argument(
        "--no-del",
        type=bool,
        dest="del",
        action="store_false",
        help="If a previous staging directory exists, keep it.",
    )
    parser.add_argument(
        "--ofhe_build",
        type=bool,
        default="False",
        action="store_true",
        help="Install OpenFHE Release build.",
    )
    parser.add_argument(
        "--no-ofhe_build",
        type=bool,
        dest="ofhe_build",
        action="store_true",
        help="Do not install OpenFHE Release build.",
    )
    parser.add_argument(
        "--hexl",
        type=bool,
        default=True,
        action="store_true",
        help="Install OpenFHE Release build.",
    )
    parser.add_argument(
        "--no-hexl",
        type=bool,
        dest="hexl",
        action="store_true",
        help="Do not install OpenFHE Release build.",
    )
    parser.set_defaults(fn=Configurator.configure)
