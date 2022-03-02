# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import docker
from docker.errors import DockerException

import tarfile
from sys import stderr
from getpass import getuser
from os import geteuid, getcwd, getuid, getgid, environ, chdir as change_directory_to
from platform import system as os_name
from pathlib import Path
from dataclasses import dataclass
from shutil import copyfile
from typing import Dict, Iterable, Optional


@dataclass(frozen=True, init=False)
class Constants:
    user: str = getuser()
    # TODO remove hardcoding of version
    base_label: str = f"{getuser()}/ubuntu_he_base:2.0.0"
    derived_label: str = f"{getuser()}/ubuntu_he_test"


def copyfiles(files: Iterable[str], src_dir: str, dst_dir: str) -> None:
    src_dir, dst_dir = Path(src_dir), Path(dst_dir)
    for filename in files:
        copyfile(src_dir / filename, dst_dir / filename)


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
        print()
        exit(1)


def archive_and_compress(
    name: str, filepaths: Iterable[str], root: Optional[str] = None
) -> None:
    """"""
    root = Path(root if root else ".")
    try:
        with tarfile.open(name, "x:gz") as tar:
            for filepath in filepaths:
                tar.add(root / filepath)
    except FileExistsError as file_exists_error:
        print(f"Error: The file '{root / filepath}' already exists")
        # then continue


def setup_docker(args):
    """Build the docker for the toolkit"""

    if args.y:
        print_preamble()

    ROOT = args.hekit_root_dir

    # set_stagging_area
    stagging_path = Path(ROOT) / "__stagging__"
    stagging_path.mkdir(exist_ok=True)

    parts_tar_gz = stagging_path / "parts.tar.gz"
    if not parts_tar_gz.exists():
        archive_and_compress(
            parts_tar_gz,
            (
                "docker/runners.sh",
                "he-samples/cmake",
                "he-samples/CMakeLists.txt",
                "he-samples/examples/",
                "he-samples/sample-kernels/",
            ),
            root=ROOT,
        )

    copyfiles(
        ("Dockerfile.base", "Dockerfile.toolkit"),
        src_dir=(ROOT / "docker"),
        dst_dir=stagging_path,
    )

    # check docker connectivity

    # build base image

    # build toolkit image


def old_stuff():

    try:
        print("\nCHECKING DOCKER FUNCTIONALITY...")
        client = docker.from_env()
    except DockerException as docker_exception:
        print("Docker Error\n", docker_exception, file=stderr)
        exit(1)

    environment: Dict[str, str] = {
        "http_proxy": environ.get("http_proxy", ""),
        "https_proxy": environ.get("https_proxy", ""),
        "socks_proxy": environ.get("socks_proxy", ""),
        "ftp_proxy": environ.get("ftp_proxy", ""),
        "no_proxy": environ.get("no_proxy", ""),
        "USER": getuser(),
    }

    print("\nCHECKING IN-DOCKER CONNECTIVITY...")
    check_conn = client.containers.run(
        volumes=[f"{getcwd()}/basic-docker-test.sh:/basic-docker-test.sh"],
        detach=True,
        stream=True,
        environment=environment,
        image="ubuntu:20.04",
        command="/bin/bash ./basic-docker-test.sh",
    )
    for stream in check_conn.logs(stream=True):
        print("[CONTAINER]", stream)
    status_code = check_conn.wait()["StatusCode"]
    if status_code != 0:
        print(
            "In-docker connectivity failing.",
            f"Return code was '{status_code}'",
            file=stderr,
        )
        exit(1)

    constants = Constants()

    if args.id:
        USERID, GROUPID = args.id, args.id
    elif os_name() == "Darwin":
        # Check for Mac OS
        print("\nWARNING: Detected Mac OSX ... ")
        USERID, GROUPID = 1000, 1000
    else:
        USERID, GROUPID = getuid(), getgid()

    print(f"\nWARNING: Setting UID/GID of docker user to '{USERID}/{GROUPID}'")

    buildargs: Dict[str, str] = {
        **environment,
        "UID": str(USERID),
        "GID": str(GROUPID),
        "UNAME": environment["USER"],
    }

    print("buildargs", buildargs)

    images: list = client.images.list(name=constants.base_label)
    if len(images) == 0:
        print("\nBUILDING BASE DOCKERFILE...")
        response = client.api.build(
            dockerfile="Dockerfile.base",
            rm=True,  # remove intermediates
            buildargs=buildargs,
            tag=constants.base_label,
            path=getcwd(),
        )
        for out in response:
            print(out)

    images: list = client.images.list(name=constants.derived_label)
    if len(images) == 0:
        print("\nBUILDING TOOLKIT DOCKERFILE...")
        response = client.api.build(
            dockerfile="Dockerfile.toolkit",
            rm=True,  # remove intermediates
            buildargs=buildargs,
            tag=constants.derived_label,
            path=getcwd(),
        )
        for out in response:
            print(out)

    print("\nRUN DOCKER CONTAINER...")
    # Python cannot relinquish control therefore advise
    print("Run container with\n", f"docker run -it {constants.derived_label}")
