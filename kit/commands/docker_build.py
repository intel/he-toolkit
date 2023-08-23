# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module sets up a docker container with the required libraries for executing FHE applications"""

from argparse import ArgumentTypeError
from re import compile as regex
from sys import stderr, exit as sys_exit
from os import getuid, getgid, environ, chdir as change_directory_to, path as os_path
from pathlib import Path
from shutil import copyfile, rmtree
from platform import system as os_name
from typing import Dict, Iterable

import toml

from kit.utils.archive import archive_and_compress
from kit.utils.constants import Constants
from kit.utils.typing import PathType

try:
    # docker-py is optional and will not be used from within a docker container
    from kit.utils.docker_tools import DockerTools, DockerException
except ImportError:

    def try_setup_docker(args):  # pylint: disable=unused-argument
        """Informs that this command can't be used due to missing dependencies"""
        print("This command is disabled. To enable it install the docker-py dependency")
        print("  pip install docker")

else:

    def try_setup_docker(args):
        """Set up the docker environment"""
        setup_docker(args)


def copyfiles(files: Iterable[PathType], src_dir: PathType, dst_dir: PathType) -> None:
    """Copies several files from a source to a destination"""
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    for filename in files:
        copyfile(src_dir / filename, dst_dir / filename)


def create_buildargs(environment: Dict[str, str], ID: int) -> Dict[str, str]:
    """Returns a dictionary of build arguments"""
    if ID:
        USERID, GROUPID = ID, ID
    elif os_name() == "Darwin":
        # Check for Mac OS
        print("WARNING: DETECTED MAC OS ... ")
        USERID, GROUPID = 1000, 1000
    else:
        USERID, GROUPID = getuid(), getgid()

    # TODO could buildargs and environment be single obj?
    return {
        **environment,
        "UID": str(USERID),
        "GID": str(GROUPID),
        "UNAME": Constants.user,
        "TOOLKIT_BASE_IMAGE": Constants.base_label,
        "VSCODE_BASE_IMAGE": Constants.toolkit_label,
    }


def create_environment():
    """Returns a dictionary of environment variables"""
    environment: Dict[str, str] = {
        "http_proxy": environ.get("http_proxy", ""),
        "https_proxy": environ.get("https_proxy", ""),
        "socks_proxy": environ.get("socks_proxy", ""),
        "ftp_proxy": environ.get("ftp_proxy", ""),
        "no_proxy": environ.get("no_proxy", ""),
        "USER": Constants.user,
    }
    return environment


def print_preamble() -> None:
    """Prints instruction about docker functionality"""
    INSTRUCTIONS: str = """

PLEASE READ ALL OF THE FOLLOWING:

The program packages the he-samples code, confirms Docker functionality,
and builds a Docker image for testing several homomorphic encryption workloads.

Please note that if you are located behind a firewall (corporate or otherwise),
make sure you have the proxies setup accordingly, i.e. environment variables
http_proxy and https_proxy are set.

"""
    print(INSTRUCTIONS)
    try:
        input(
            "If you want to proceed, press enter to continue. "
            "Otherwise, exit with Ctrl+C "
        )
    except KeyboardInterrupt:
        print()  # newline
        sys_exit(1)


def filter_file_list(file_list: Iterable[str]) -> Iterable[str]:
    """Filter out comment lines and empty lines"""
    comments_or_empty = regex(r"^\s*#|^\s*$")
    return (
        filename.rstrip()
        for filename in file_list
        if not comments_or_empty.search(filename)
    )


def create_tar_gz_file(
    toolkit_tar_gz: PathType, archived_files: PathType, ROOT: PathType
) -> None:
    """Archive several files in a tar.gz file"""
    toolkit_tar_gz = Path(toolkit_tar_gz)
    if not toolkit_tar_gz.exists():
        print("MAKING TOOLKIT.TAR.GZ ...")
        with open(archived_files, encoding="utf-8") as f:
            try:
                archive_and_compress(toolkit_tar_gz, filter_file_list(f), root=ROOT)
            except FileExistsError as file_exists_error:
                print(file_exists_error)
                # then continue


def setup_docker(args):
    """Build the docker for the toolkit"""
    ROOT = Constants.HEKIT_ROOT_DIR
    docker_filepaths = ROOT / "docker"
    staging_path = ROOT / "__staging__"

    if args.clean:
        try:
            rmtree(staging_path)
        except FileNotFoundError:
            pass
        print("Staging area deleted")
        sys_exit(0)

    if args.y:
        print_preamble()

    try:
        print("CHECKING DOCKER FUNCTIONALITY ...")
        docker_tools = DockerTools()
    except DockerException as docker_exception:
        print("Docker Error\n", docker_exception, file=stderr)
        sys_exit(1)

    environment = create_environment()

    if args.check_only:
        print("CHECKING IN-DOCKER CONNECTIVITY ...")
        # Assume we are in he-toolkit directory
        docker_tools.test_connection(
            environment=environment,
            scriptpath=docker_filepaths / "basic-docker-test.sh",
        )
        sys_exit(0)

    # set_staging_area
    staging_path.mkdir(exist_ok=True)

    toolkit_tar_gz = staging_path / "toolkit.tar.gz"
    archived_files = docker_filepaths / "which-files.txt"
    create_tar_gz_file(toolkit_tar_gz, archived_files, ROOT)

    change_directory_to(staging_path)

    buildargs = create_buildargs(environment, args.id)

    print(
        f"WARNING: Setting UID/GID of docker user to '{buildargs['UID']}/{buildargs['GID']}'"
    )

    features = {
        "base": f"{docker_filepaths}/Dockerfile.base",
        "toolkit": f"{docker_filepaths}/Dockerfile.toolkit",
    }

    if isinstance(args.enable, dict):
        features.update(args.enable)

    prev = "ubuntu:22.04"
    # Must make sure we have a platform image
    if docker_tools.image_exists(prev):
        docker_tools.pull_base_image(prev)

    for feature, path in features.items():
        print("BUILDING", feature.upper(), "DOCKERFILE ...")
        current = Constants.custom_label % feature
        print("BUILDING", current, "FROM", prev)
        buildargs["CUSTOM_FROM"] = prev
        docker_tools.try_build_new_image(
            dockerfile=path,
            tag=current,
            buildargs=buildargs,
        )
        prev = current

    print("RUN DOCKER CONTAINER ...")
    print("Run container with")
    if isinstance(args.enable, dict) and "vscode" in args.enable:
        print("docker run -d -p <ip addr>:<port>:8888", Constants.vscode_label)
        print("Then to open vscode navigate to <ip addr>:<port> in your chosen browser")
    else:
        print("docker run -it", Constants.toolkit_label)


def get_docker_features(keys: str) -> Dict[str, str]:
    """Transform string of comma seperated features to enable into a dict with
    the keys as feature strings and values as locoations of the necessary
    Dockerfile"""
    tobj = toml.load(Constants.HEKIT_DOCKER_DIR / "dockerfiles.toml")
    key_list = list(map(str.strip, keys.split(",")))
    not_found = set(key_list) - set(tobj.keys())
    if len(not_found) > 0:
        keystr = ", ".join(not_found)
        raise ArgumentTypeError(
            f"Input key(s) `{keystr}` not found in accepted list of keys in `dockerfiles.toml`"
        )
    return {key: os_path.expandvars(tobj[key]) for key in key_list}


def get_feature_names() -> tuple[str, ...]:
    """Read `dockerfiles.toml` and return a list of the keys"""
    tobj = toml.load(Constants.HEKIT_DOCKER_DIR / "dockerfiles.toml")
    return tuple(tobj.keys())


def set_docker_subparser(subparsers):
    """create the parser for the 'docker-build' command"""
    parser_docker_build = subparsers.add_parser(
        "docker-build", description="docker build of the toolkit"
    )
    parser_docker_build.add_argument("--id", type=int, help="custom user and group id")
    parser_docker_build.add_argument(
        "--clean", action="store_true", help="delete staging"
    )
    # TODO Maybe should be its own subcommand?
    parser_docker_build.add_argument(
        "--check-only", action="store_true", help="only run container for proxy checks"
    )
    parser_docker_build.add_argument(
        "--enable",
        type=get_docker_features,
        help=f"add/enable extra features in docker build of toolkit, choose from {get_feature_names()}",
    )
    parser_docker_build.add_argument(
        "-y", action="store_false", help="say yes to prompts"
    )
    parser_docker_build.set_defaults(fn=try_setup_docker)
