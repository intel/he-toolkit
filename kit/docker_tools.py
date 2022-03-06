# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import docker
from docker.errors import DockerException

import json
from os import getcwd
from sys import stderr
from pathlib import Path
from typing import Dict


class DockerBuildError(Exception):
    """Exception for something wrong with the docker build."""

    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


def check_build(image):
    """For use as a decorator.
    Forward the build info, but check for error in build.
    If found raise exception"""

    def inner(*args, **kwargs):
        responses = image(*args, **kwargs)
        for response in map(json.loads, responses):
            if "stream" in response.keys():
                yield response["stream"]
            elif "error" in response.keys():
                raise DockerBuildError("Docker build failed", response)
            else:
                raise DockerBuildError("Unrecognised stream property", response)

    return inner


class DockerTools:
    def __init__(self):
        self.client = docker.from_env()

    # TODO remove printing out to command file
    # Or move this method back into command file
    def checks(self, environment) -> None:

        check_conn = self.run_script_in_container(
            # Assume we are in he-toolkit directory
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

    def image_exists(self, image_name: str) -> bool:
        """Returns True if image already exists otherwise False"""
        images = self.client.images.list(name=image_name)
        return len(images) > 0

    @check_build
    def build_image(self, dockerfile: str, tag: str, buildargs):
        """Build images as we like them built"""
        return self.client.api.build(
            dockerfile=dockerfile,
            rm=True,  # remove intermediates
            buildargs=buildargs,
            tag=tag,
            path=getcwd(),
        )

    def run_script_in_container(
        self, environment, scriptpath, image="ubuntu:20.04"
    ) -> int:
        scriptsrc = Path(scriptpath).expanduser().resolve()
        return self.client.containers.run(
            volumes=[f"{scriptsrc}:/script"],
            detach=True,
            stream=True,
            environment=environment,
            image=image,
            command="/bin/bash /script",
        )
