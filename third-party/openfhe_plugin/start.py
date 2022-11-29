import os.path
from os import path

from openfhe.configurator import Configurator


def set_openfhe_subparser(subparsers):
    parser = subparsers.add_parser("openfhe", description="OpenFHE configurator WIP")
    parser.add_argument(
        "--delete",
        default=True,
        action="store_true",
        help="If a previous staging directory exists, DELETE.",
    )
    parser.add_argument(
        "--no-delete",
        dest="delete",
        action="store_false",
        help="If a previous staging directory exists, KEEP.",
    )
    parser.add_argument(
        "--ofhe",
        default=False,
        action="store_true",
        help="Install OpenFHE Release build.",
    )
    parser.add_argument(
        "--no-ofhe",
        dest="ofhe",
        action="store_false",
        help="DO NOT install OpenFHE Release build.",
    )
    parser.add_argument(
        "--hexl", default=True, action="store_true", help="Install HEXL build."
    )
    parser.add_argument(
        "--no-hexl",
        dest="hexl",
        action="store_false",
        help="DO NOT install HEXL build.",
    )
    parser.set_defaults(fn=Configurator.configure)
