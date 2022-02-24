#! /usr/bin/python3

# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import docker

import tarfile
from sys import stderr, argv
from getpass import getuser
from os import geteuid, getcwd, getuid, getguid
from os import chdir as change_directory_to
from platform import system as os_name
from pathlib import Path
from dataclasses import dataclass

ROOT : Path = Path("..").resolve()

INSTRUCTIONS : str = """

PLEASE READ ALL OF THE FOLLOWING INSTRUCTIONS:

The following script package the he-samples code, confirm Docker functionality,
and build/run a Docker for testing several homomorphic encryption workloads.

Do note that this script has a few usage requirements:
    1. This script MUST BE RUN as a user BESIDES root.
    2. It must be run from its own base directory
    3. If you are located behind a firewall (corporate or otherwise),
    please make sure you have the proxies setup accordingly
    (e.g. environment variables: http_proxy and https_proxy are set).

"""

try:
    input("If understood, press enter to continue. Otherwise, exit with Ctrl+C")
except KeyboardInterrupt:
    exit(1)

if geteuid() == 0:
    print("Error: Please run this script as non-root")
    exit(1)

try:
    def exclude_build_directory(tarinfo):
        if tarinfo.name.startswith("he-samples/build"):
            return None
        else:
            return tarinfo

    with tarfile.open("parts.tar.gz", "x:gz") as tar:
        tar.add("runners")
        old_directory = getcwd()
        change_directory_to(ROOT)
        tar.add("he-samples", filter=exclude_build_directory)
        for directory in ("kit", "recipes", "default.config"):
            tar.add(directory)
        change_directory_to(old_directory)
except FileExistsError as file_exists_error:
    print(file_exists_error)
    # then continue



try:
    print("\nCHECKING DOCKER FUNCTIONALITY...")
    client = docker.from_env()
except DockerException as docker_exception:
    print("Docker Error\n", docker_exception, file=stderr)
    exit(1)

# TODO
print("\nCHECKING IN-DOCKER CONNECTIVITY...")
if not docker.run -v \
  "$PWD"/basic-docker-test.sh:/basic-docker-test.sh \
  --env-file ./env.list \
  ubuntu:bionic \
  /bin/bash \
  /basic-docker-test.sh:
  print("In-docker connectivity failing.", file=stderr)
  exit(1)

@dataclass(frozen=True, init=False)
class NS:
    user: str = getuser()
    # TODO remove hardcoding of version
    version : int = 2.0.0
    base_label: str = f"{user}/ubuntu_he_base:{version}"
    derived_label: str = f"{user}/ubuntu_he_test"

USERID = getuid()
GROUPID = getguid()

# Check for Mac OSX
if os_name() == "Darwin":
  if argv[1] == 0:
      print("\nWARNING: Detected Mac OSX... Changing UID/GID of docker user to 1000")
      USERID = 1000
      GROUPID = 1000
  else
      print(f"\nWARNING: Changing UID/GID of docker user to '{argv[1]}'")
      GROUPID = argv[1]
      GROUPID = argv[1]

#TODO
images : list = client.images.list(name=base_label)
if images:
    print("\nBUILDING BASE DOCKERFILE...")
    client.images.build(
      buildargs={"http_proxy":"",
                 "https_proxy":"",
                 "socks_proxy":"",
                 "ftp_proxy":"" ,
                 "no_proxy":"",
                 "UID":USERID,
                 "GID":GROUPID,
                 "UNAME"=user},
      tag=base_label,
      dockerfile="Dockerfile.base",
      path=getcwd())

print("\nBUILDING TOOLKIT DOCKERFILE...")
#TODO
client.images.build(
  buildargs={"UNAME":user},
  tag=derived_label,
  dockerfile=Dockerfile.toolkit,
  path=getcwd())

print("\nRUN DOCKER CONTAINER...")
# Python cannot relinquish control therefore advise
print("Run container with\n", f"docker run -it {derived_label}")
