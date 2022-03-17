# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from docker import from_env as docker_from_env
from docker.errors import DockerException

import json
from sys import stderr
from pathlib import Path


class DockerBuildError(Exception):
    """Exception for something wrong with the docker build."""

    def __init__(self, message, error):
        super().__init__(message)
        self.error = error


def check_build(func):
    """For use as a decorator.
    Forward the build info, but check for error in build.
    If found raise exception"""

    def inner(*args, **kwargs):
        responses = func(*args, **kwargs)
        for response in map(json.loads, responses):
            if "stream" in response.keys():
                yield response["stream"]
            elif "aux" in response.keys() and "ID" in response["aux"]:
                yield response["aux"]["ID"]
            elif "error" in response.keys():
                raise DockerBuildError("Docker build failed", response)
            else:
                raise DockerBuildError("Unrecognised stream property", response)

    return inner


def simple_container_logs(func):
    """Simplifies a container output to give logs and when exahsted
    provide the status code on exit"""

    def inner(*args, **kwargs):
        container = func(*args, **kwargs)
        for log in container.logs(stream=True):
            yield log, None
        yield None, container.wait()["StatusCode"]

    return inner


class DockerTools:
    def __init__(self):
        self.client = docker_from_env()

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
            path=".",
        )

    @simple_container_logs
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
