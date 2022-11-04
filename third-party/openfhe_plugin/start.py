import os.path
from os import path

from openfhe_plugin.configurator import Configurator


def set_openfhe_subparser(subparsers):
    parser = subparsers.add_parser("openfhe", description="OpenFHE configurator")
    parser.add_argument(
        "exists",
        help="If a previous staging directory exists, delete? [y/n] : ",
        required=False,
    )
    parser.add_argument(
        "of_build", help="Would you like an OpenFHE Release build?     [y/n] : "
    )
    parser.add_argument(
        "hexl_build", help="Would you like a HEXL build?                 [y/n] : "
    )
    parser.set_defaults(fn=Configurator.configure)
