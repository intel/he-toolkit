# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import docker
from docker.errors import DockerException

import tarfile
from re import search
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
        print()  # newline
        exit(1)


def archive_and_compress(
    name: str, filepaths: Iterable[str], root: Optional[str] = None
) -> None:
    """Archive and compress files and directories into tar.gz file"""
    root = Path(root if root else ".")
    try:
        with tarfile.open(name, "x:gz") as tar:
            for filepath in filepaths:
                tar.add(root / filepath, arcname=filepath)
    except FileExistsError as file_exists_error:
        print(f"Error: The file '{root / filepath}' already exists")
        # then continue


def filter_file_list(file_list: Iterable[str]) -> Iterable[str]:
    """"""
    for filename in file_list:
        # filter out comment lines and empty lines
        if not search("^\s*#|^\s*$", filename):
            yield filename.rstrip()


def setup_docker(args):
    """Build the docker for the toolkit"""

    if args.y:
        print_preamble()

    environment: Dict[str, str] = {
        "http_proxy": environ.get("http_proxy", ""),
        "https_proxy": environ.get("https_proxy", ""),
        "socks_proxy": environ.get("socks_proxy", ""),
        "ftp_proxy": environ.get("ftp_proxy", ""),
        "no_proxy": environ.get("no_proxy", ""),
        "USER": getuser(),
    }

    if args.check_only:
        try:
            print("CHECKING DOCKER FUNCTIONALITY ...")
            client = docker.from_env()
        except DockerException as docker_exception:
            print("Docker Error\n", docker_exception, file=stderr)
            exit(1)

        print("CHECKING IN-DOCKER CONNECTIVITY ...")
        docker_checks(client, environment)
        exit(0)

    ROOT = args.hekit_root_dir

    # set_stagging_area
    stagging_path = Path(ROOT) / "__stagging__"
    stagging_path.mkdir(exist_ok=True)

    parts_tar_gz = stagging_path / "parts.tar.gz"
    if not parts_tar_gz.exists():
        print("MAKING PARTS.TAR.GZ ...")
        with open(ROOT / "docker/which_files.txt") as f:
            archive_and_compress(parts_tar_gz, filter_file_list(f), root=ROOT)

    copyfiles(
        ("Dockerfile.base", "Dockerfile.toolkit"),
        src_dir=(ROOT / "docker"),
        dst_dir=stagging_path,
    )

    change_directory_to(stagging_path)

    try:
        print("CHECKING DOCKER FUNCTIONALITY ...")
        client = docker.from_env()
    except DockerException as docker_exception:
        print("Docker Error\n", docker_exception, file=stderr)
        exit(1)

    # build base image
    # build toolkit image
    build_toolkit_images(client, args, environment)


def run_script_in_container(
    containers, environment, scriptpath, image="ubuntu:20.04"
) -> int:
    scriptsrc = Path(scriptpath).expanduser().resolve()
    print(f"ssrc and sdst {scriptsrc}, {scriptdst}")
    return containers.run(
        volumes=[f"{scriptsrc}:/script"],
        detach=True,
        stream=True,
        environment=environment,
        image=image,
        command="/bin/bash /script",
    )


def docker_checks(client, environment) -> None:

    check_conn = run_script_in_container(
        # Assume we are in he-toolkit directory
        client.containers,
        environment,
        "./docker/basic-docker-test.sh",
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


def image_exists(client, image_name: str) -> bool:
    """Returns True if image already exists otherwise False"""
    images = client.images.list(name=image_name)
    return len(images) > 0


def check_build(image):
    """For use as a decorator.
    Forward the build info, but check for error in build.
    If found raise exception"""
    # TODO atm, only forwards

    return image


@check_build
def build_image(client, dockerfile: str, tag: str, buildargs):
    """Build images as we like them built"""
    return client.api.build(
        dockerfile=dockerfile,
        rm=True,  # remove intermediates
        buildargs=buildargs,
        tag=tag,
        path=getcwd(),
    )


def build_toolkit_images(client, args, environment) -> None:

    if args.id:
        USERID, GROUPID = args.id, args.id
    elif os_name() == "Darwin":
        # Check for Mac OS
        print("WARNING: DETECTED MAC OS ... ")
        USERID, GROUPID = 1000, 1000
    else:
        USERID, GROUPID = getuid(), getgid()

    print(f"WARNING: Setting UID/GID of docker user to '{USERID}/{GROUPID}'")

    # TODO could buildargs and environment be single obj?
    buildargs: Dict[str, str] = {
        **environment,
        "UID": str(USERID),
        "GID": str(GROUPID),
        "UNAME": environment["USER"],
    }

    print("buildargs", buildargs)
    constants = Constants()

    if not image_exists(client, constants.base_label):
        print("BUILDING BASE DOCKERFILE ...")
        response = build_image(
            client,
            dockerfile="Dockerfile.base",
            tag=constants.base_label,
            buildargs=buildargs,
        )
        for out in response:
            print(out)

    if not image_exists(client, constants.derived_label):
        print("BUILDING TOOLKIT DOCKERFILE...")
        response = build_image(
            client,
            dockerfile="Dockerfile.toolkit",
            tag=constants.derived_label,
            buildargs=buildargs,
        )
        for out in response:
            print(out)

    print("RUN DOCKER CONTAINER...")
    # Python cannot relinquish control therefore advise
    print("Run container with")
    print(f"docker run -it {constants.derived_label}")
