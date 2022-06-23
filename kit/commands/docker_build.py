# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module sets up a docker container with the required libraries for executing FHE applications"""

from re import search
from sys import stderr, exit as sys_exit
from os import getuid, getgid, environ, chdir as change_directory_to
from pathlib import Path
from shutil import copyfile, rmtree
from platform import system as os_name
from typing import Dict, Iterable
from kit.utils.archive import archive_and_compress  # pylint: disable=no-name-in-module
from kit.utils.constants import Constants  # pylint: disable=no-name-in-module
from kit.utils.typing import PathType

try:
    # docker-py is optional and will not be used from within a docker container
    from kit.utils.docker_tools import (  # pylint: disable=no-name-in-module
        DockerTools,
        DockerException,
    )
except ImportError:

    def try_setup_docker(args):  # pylint: disable=unused-argument
        """Informs that this command can't be used due to missing dependencies"""
        print("This command is disabled. To enable it install the docker-py dependency")
        print("  pip install docker")


else:

    def try_setup_docker(args):
        """Set up the docker environment"""
        setup_docker(args)


def copyfiles(files: Iterable[str], src_dir: str, dst_dir: str) -> None:
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
    for filename in file_list:
        if not search(r"^\s*#|^\s*$", filename):
            yield filename.rstrip()


def create_tar_gz_file(
    toolkit_tar_gz: PathType, archived_files: str, ROOT: str
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
    ROOT = Path(args.hekit_root_dir)
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

    files_to_copy = ["Dockerfile.base", "Dockerfile.toolkit"]
    if args.enable == "vscode":
        files_to_copy.append("Dockerfile.vscode")
    copyfiles(files_to_copy, src_dir=docker_filepaths, dst_dir=staging_path)

    change_directory_to(staging_path)

    buildargs = create_buildargs(environment, args.id)

    print(
        f"WARNING: Setting UID/GID of docker user to '{buildargs['UID']}/{buildargs['GID']}'"
    )

    print("BUILDING BASE DOCKERFILE ...")
    docker_tools.try_build_new_image(
        dockerfile="Dockerfile.base", tag=Constants.base_label, buildargs=buildargs
    )

    print("BUILDING TOOLKIT DOCKERFILE ...")
    docker_tools.try_build_new_image(
        dockerfile="Dockerfile.toolkit",
        tag=Constants.toolkit_label,
        buildargs=buildargs,
    )

    if args.enable == "vscode":
        print("BUILDING VSCODE DOCKERFILE ...")
        docker_tools.try_build_new_image(
            dockerfile="Dockerfile.vscode",
            tag=Constants.vscode_label,
            buildargs=buildargs,
        )

    print("RUN DOCKER CONTAINER ...")
    print("Run container with")
    if args.enable == "vscode":
        print(f"docker run -d -p <ip addr>:<port>:8888 {Constants.vscode_label}")
        print("Then to open vscode navigate to <ip addr>:<port> in your chosen browser")
    else:
        print(f"docker run -it {Constants.toolkit_label}")


def set_docker_subparser(subparsers, hekit_root_dir):
    """create the parser for the 'docker-build' command"""
    parser_docker_build = subparsers.add_parser(
        "docker-build", description="docker build of the toolkit"
    )
    parser_docker_build.add_argument("--id", type=int, help="custom user and group id")
    parser_docker_build.add_argument(
        "--clean", action="store_true", help="delete staging"
    )
    # FIXME should this be its own subcommand?
    parser_docker_build.add_argument(
        "--check-only", action="store_true", help="only run container for proxy checks"
    )
    # In future change to accept several strings
    parser_docker_build.add_argument(
        "--enable",
        type=str,
        choices=["vscode"],
        help="add/enable extra features in docker build of toolkit",
    )
    parser_docker_build.add_argument(
        "-y", action="store_false", help="say yes to prompts"
    )
    parser_docker_build.set_defaults(fn=try_setup_docker, hekit_root_dir=hekit_root_dir)
