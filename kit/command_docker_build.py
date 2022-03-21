# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from re import search
from sys import stderr
from getpass import getuser
from os import getuid, getgid, environ, chdir as change_directory_to
from dataclasses import dataclass
from pathlib import Path
from shutil import copyfile, rmtree
from platform import system as os_name
from typing import Dict, Iterable

from archive import archive_and_compress
from docker_tools import DockerTools, DockerException


@dataclass(frozen=True, init=False)
class Constants:
    user: str = getuser()
    # TODO remove hardcoding of version
    base_label: str = f"{getuser()}/ubuntu_he_base:2.0.0"
    derived_label: str = f"{getuser()}/ubuntu_he_test"
    vscode_label: str = f"{getuser()}/ubuntu_he_vscode"


def copyfiles(files: Iterable[str], src_dir: str, dst_dir: str) -> None:
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    for filename in files:
        copyfile(src_dir / filename, dst_dir / filename)


def create_buildargs(environment: Dict[str, str], ID: int) -> Dict[str, str]:
    """"""
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
        "UNAME": environment["USER"],
    }


def create_environment():
    """"""
    environment: Dict[str, str] = {
        "http_proxy": environ.get("http_proxy", ""),
        "https_proxy": environ.get("https_proxy", ""),
        "socks_proxy": environ.get("socks_proxy", ""),
        "ftp_proxy": environ.get("ftp_proxy", ""),
        "no_proxy": environ.get("no_proxy", ""),
        "USER": getuser(),
    }
    return environment


def print_preamble() -> None:
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
        exit(1)


def filter_file_list(file_list: Iterable[str]) -> Iterable[str]:
    """"""
    for filename in file_list:
        # filter out comment lines and empty lines
        if not search("^\s*#|^\s*$", filename):
            yield filename.rstrip()


def create_tar_gz_file(toolkit_tar_gz: str, archived_files: str, ROOT: str):
    """"""
    if not toolkit_tar_gz.exists():
        print("MAKING TOOLKIT.TAR.GZ ...")
        with open(archived_files) as f:
            root = ROOT
            try:
                archive_and_compress(toolkit_tar_gz, filter_file_list(f), root)
            except FileExistsError as file_exists_error:
                print(f"Error: The file '{root / filepath}' already exists")
                # then continue


def setup_docker(args):
    """Build the docker for the toolkit"""

    ROOT = Path(args.hekit_root_dir)
    docker_filepaths = ROOT / "docker"
    stagging_path = ROOT / "__stagging__"

    if args.clean:
        rmtree(stagging_path)
        print("Stagging area deleted")
        exit(0)

    if args.y:
        print_preamble()

    try:
        print("CHECKING DOCKER FUNCTIONALITY ...")
        docker_tools = DockerTools()
    except DockerException as docker_exception:
        print("Docker Error\n", docker_exception, file=stderr)
        exit(1)

    environment = create_environment()

    if args.check_only:
        print("CHECKING IN-DOCKER CONNECTIVITY ...")
        # Assume we are in he-toolkit directory
        docker_tools.test_connection(
            environment=environment,
            scriptpath=docker_filepaths / "basic-docker-test.sh",
        )
        exit(0)

    # set_stagging_area
    stagging_path.mkdir(exist_ok=True)

    toolkit_tar_gz = stagging_path / "toolkit.tar.gz"
    archived_files = docker_filepaths / "which-files.txt"
    create_tar_gz_file(toolkit_tar_gz, archived_files, ROOT)

    files_to_copy = ["Dockerfile.base", "Dockerfile.toolkit"]
    if args.enable == "vscode":
        files_to_copy.append("Dockerfile.vscode")
    copyfiles(files_to_copy, src_dir=docker_filepaths, dst_dir=stagging_path)

    change_directory_to(stagging_path)

    constants = Constants()

    buildargs = create_buildargs(environment, args.id)

    print(
        f"WARNING: Setting UID/GID of docker user to '{buildargs['UID']}/{buildargs['GID']}'"
    )

    print("BUILDING BASE DOCKERFILE ...")
    docker_tools.try_build_new_image(
        dockerfile="Dockerfile.base", tag=constants.base_label, buildargs=buildargs
    )

    print("BUILDING TOOLKIT DOCKERFILE ...")
    docker_tools.try_build_new_image(
        dockerfile="Dockerfile.toolkit",
        tag=constants.derived_label,
        buildargs=buildargs,
    )

    if args.enable == "vscode":
        print("BUILDING VSCODE DOCKERFILE ...")
        docker_tools.try_build_new_image(
            dockerfile="Dockerfile.vscode",
            tag=constants.vscode_label,
            buildargs=buildargs,
        )

    print("RUN DOCKER CONTAINER ...")
    print("Run container with")
    if args.enable == "vscode":
        print(f"docker run -d -p 8888:8888 {constants.vscode_label}")
        print("Then to open vscode navigate to localhost:8888 in your chosen browser")
    else:
        print(f"docker run -it {constants.derived_label}")
