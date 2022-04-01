# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from os import getcwd, chdir
from getpass import getuser

from .context import hekit, command_docker_build, docker_tools
from hekit import main
from command_docker_build import setup_docker

# Due to install command changes current directory,
# the other commands need to restore the current path
cwd_test = getcwd()


def test_docker_build_check_build(mocker):
    """Arrange"""
    args = MockArgs(check_only=False, clean=False, enable=None)
    client = MockClient()
    derived_label = f"{getuser()}/ubuntu_he_toolkit:2.0.0"

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    # Mocking objects from command_docker_build
    mock_input = mocker.patch("command_docker_build.input")
    mock_input.return_value = "a"
    mock_print_build = mocker.patch("command_docker_build.print")
    # Mocking objects from docker_tools
    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client
    mock_print_tools = mocker.patch("docker_tools.print")

    """Act"""
    main()

    """Assert"""
    mock_print_build.assert_any_call("BUILDING BASE DOCKERFILE ...")
    mock_print_build.assert_any_call("BUILDING TOOLKIT DOCKERFILE ...")
    mock_print_build.assert_any_call(f"docker run -it {derived_label}")
    mock_print_tools.assert_any_call(client.value.replace('"', ""))


def test_docker_build_check_enable(mocker, restore_pwd):
    """Arrange"""
    args = MockArgs(check_only=False, clean=False, enable="vscode")
    client = MockClient()

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    # Mocking objects from command_docker_build
    mock_input = mocker.patch("command_docker_build.input")
    mock_input.return_value = "a"
    mock_print_build = mocker.patch("command_docker_build.print")
    # Mocking objects from docker_tools
    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client
    mock_print_tools = mocker.patch("docker_tools.print")

    """Act"""
    main()

    """Assert"""
    mock_print_build.assert_any_call("BUILDING BASE DOCKERFILE ...")
    mock_print_build.assert_any_call("BUILDING TOOLKIT DOCKERFILE ...")
    mock_print_build.assert_any_call("BUILDING VSCODE DOCKERFILE ...")
    mock_print_build.assert_any_call(
        "Then to open vscode navigate to <ip addr>:<port> in your chosen browser"
    )
    mock_print_tools.assert_any_call(client.value.replace('"', ""))


def test_docker_build_check_only(mocker, restore_pwd):
    """Arrange"""
    args = MockArgs(check_only=True, clean=False, enable=None)
    client = MockClient()

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    # Mocking objects from command_docker_build
    mock_input = mocker.patch("command_docker_build.input")
    mock_input.return_value = "a"
    mock_print_build = mocker.patch("command_docker_build.print")
    # Mocking objects from docker_tools
    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client
    mock_print_tools = mocker.patch("docker_tools.print")

    """Act"""
    with pytest.raises(SystemExit) as exc_info:
        main()

    """Assert"""
    mock_print_build.assert_any_call("CHECKING IN-DOCKER CONNECTIVITY ...")
    mock_print_tools.assert_any_call("[CONTAINER]", client.log.decode("utf-8"), end="")
    mock_print_tools.assert_any_call("[CONTAINER]", "\n", end="")
    assert exc_info.value.code == 0


def test_docker_build_clean(mocker, restore_pwd):
    """Arrange"""
    args = MockArgs(check_only=False, clean=True, enable=None)
    client = MockClient()

    # Mocking command line args
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args, ""
    # Mocking objects from command_docker_build
    mock_input = mocker.patch("command_docker_build.input")
    mock_input.return_value = "a"
    mock_print_build = mocker.patch("command_docker_build.print")
    # Mocking objects from docker_tools
    mock_from_env = mocker.patch("docker_tools.docker_from_env")
    mock_from_env.return_value = client

    """Act"""
    with pytest.raises(SystemExit) as exc_info:
        main()

    """Assert"""
    mock_print_build.assert_any_call("Staging area deleted")
    assert exc_info.value.code == 0


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, check_only, clean, enable):
        self.check_only = check_only
        self.clean = clean
        self.enable = enable
        self.config = "tests/config/default.config"
        self.hekit_root_dir = Path(__file__).resolve().parent.parent
        self.fn = setup_docker
        self.id = None
        self.version = False
        self.y = True


class MockClient:
    def __init__(self):
        self.key = f'"stream"'
        self.value = f'"Step 1/1 : ARG UNAME"'
        self.api = API(self.key, self.value)
        self.list = []
        self.images = Images(self.list)
        self.log = b"A generic log"
        self.code = 0
        self.containers = Container(self.log, self.code)


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


@pytest.fixture
def restore_pwd():
    global cwd_test
    chdir(cwd_test)
