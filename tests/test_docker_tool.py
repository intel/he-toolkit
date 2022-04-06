# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from .context import docker_tools
from docker_tools import DockerTools, DockerBuildError


def test_build_image_response_stream(mocker):
    """Arrange"""
    key = f'"stream"'
    value = f'"Step 1/1 : ARG UNAME"'
    client = Client()
    client.set_API(key, value)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    response = act_docker.build_image("", "", [])

    """Assert"""
    assert next(response) == value.replace('"', "")


def test_build_image_response_aux(mocker):
    """Arrange"""
    key = f'"aux"'
    value_ID = f'"56987154"'
    value = f'{{"ID" : {value_ID}}}'
    client = Client()
    client.set_API(key, value)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    response = act_docker.build_image("", "", [])

    """Assert"""
    assert next(response) == value_ID.replace('"', "")


def test_build_image_response_error(mocker):
    """Arrange"""
    key = f'"error"'
    value = f'"Step 1/1 : ARG UNAME"'
    client = Client()
    client.set_API(key, value)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    with pytest.raises(DockerBuildError) as exc_info:
        response = act_docker.build_image("", "", [])
        next(response)

    """Assert"""
    assert "Docker build failed" == str(exc_info.value)


def test_build_image_response_other(mocker):
    """Arrange"""
    key = f'"other"'
    value = f'"Step 1/1 : ARG UNAME"'
    client = Client()
    client.set_API(key, value)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    with pytest.raises(DockerBuildError) as exc_info:
        response = act_docker.build_image("", "", [])
        next(response)

    """Assert"""
    assert "Unrecognized stream property" == str(exc_info.value)


def test_image_exists_empty_list(mocker):
    """Arrange"""
    list = []
    client = Client()
    client.set_images(list)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    response = act_docker.image_exists("")

    """Assert"""
    assert response == False


def test_image_exists_not_empty_list(mocker):
    """Arrange"""
    list = ["something"]
    client = Client()
    client.set_images(list)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    response = act_docker.image_exists("")

    """Assert"""
    assert response == True


def test_image_exists_some_elements_list(mocker):
    """Arrange"""
    list = ["something", "other"]
    client = Client()
    client.set_images(list)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    response = act_docker.image_exists("")

    """Assert"""
    assert response == True


def test_run_script_in_container_normal_execution(mocker):
    """Arrange"""
    exp_log = b"A generic log"
    exp_code = "4545"
    client = Client()
    client.set_container(exp_log, exp_code)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    act_docker = DockerTools()
    response = act_docker.run_script_in_container([], "")

    """Assert"""
    act_log, _ = next(response)
    _, act_code = next(response)
    assert act_log == exp_log
    assert act_code == exp_code


def test_try_build_new_image_build_skipped(mocker):
    """Arrange"""
    list = ["something"]
    client = Client()
    client.set_images(list)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client
    mock_print = mocker.patch("docker_tools.print")

    """Act"""
    act_docker = DockerTools()
    act_docker.try_build_new_image([], "", "")

    """Assert"""
    mock_print.assert_not_called()


def test_try_build_new_image_build_executed(mocker):
    """Arrange"""
    list = []
    key = f'"stream"'
    value = f'"Step 1/1 : ARG UNAME"'
    client = Client()
    client.set_images(list)
    client.set_API(key, value)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client
    mock_print = mocker.patch("docker_tools.print")

    """Act"""
    act_docker = DockerTools()
    act_docker.try_build_new_image([], "", "")

    """Assert"""
    mock_print.assert_called_once_with(value.replace('"', ""))


def test_test_connection_no_error(mocker):
    """Arrange"""
    exp_log = b"A generic log"
    exp_code = 0
    client = Client()
    client.set_container(exp_log, exp_code)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client
    mock_print = mocker.patch("docker_tools.print")
    mock_exit = mocker.patch("docker_tools.sys_exit")

    """Act"""
    act_docker = DockerTools()
    act_docker.test_connection("", "")

    """Assert"""
    exp_arg = exp_log.decode("utf-8").replace('"', "")
    mock_print.assert_any_call("[CONTAINER]", exp_arg, end="")
    mock_exit.assert_not_called()


def test_test_connection_error(mocker):
    """Arrange"""
    exp_log = b"A generic log"
    exp_code = 23
    client = Client()
    client.set_container(exp_log, exp_code)

    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client
    mock_print = mocker.patch("docker_tools.print")
    mock_exit = mocker.patch("docker_tools.sys_exit")

    """Act"""
    act_docker = DockerTools()
    act_docker.test_connection("", "")

    """Assert"""
    mock_print.assert_any_call("[CONTAINER]", "\n", end="")
    mock_exit.assert_called_once_with(1)


"""Utilities used by the tests"""


class Client:
    def set_API(self, key, value):
        self.api = API(key, value)

    def set_images(self, image_name):
        self.images = Images(image_name)

    def set_container(self, logs, stauts_code):
        self.containers = Container(logs, stauts_code)


class API:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def build(self, dockerfile, rm, buildargs, tag, path):
        str_key_value = f"{{{self.key} : {self.value}}}"
        return iter([str_key_value])


class Images:
    def __init__(self, image_list):
        self.image_list = image_list

    def list(self, name):
        return self.image_list


class Container:
    class Container_return:
        def __init__(self, log, stauts_code):
            self.log = log
            self.stauts_code = stauts_code

        def logs(self, stream):
            return iter([self.log])

        def wait(self):
            return {"Error": None, "StatusCode": self.stauts_code}

    def __init__(self, logs, stauts_code):
        self.result = self.Container_return(logs, stauts_code)

    def run(self, volumes, detach, stream, environment, image, command):
        return self.result
