# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from os import getcwd, chdir, path as os_path
from getpass import getuser

from kit.hekit import main
from kit.commands.docker_build import setup_docker

# Due to install command changes current directory,
# the other commands need to restore the current path
cwd_test = getcwd()


def test_docker_build_check_build(mocker):
    derived_label = f"{getuser()}/ubuntu_he_toolkit:2.0.0"
    args = MockArgs(check_only=False, clean=False, enable=None)
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""

    main()
    assert 1 == mockers.mock_create_tar_gz.call_count
    assert 1 == mockers.mock_change_dir.call_count
    assert 1 == mockers.mock_mkdir.call_count
    mockers.mock_print_build.assert_any_call("BUILDING", "BASE", "DOCKERFILE ...")
    mockers.mock_print_build.assert_any_call("BUILDING", "TOOLKIT", "DOCKERFILE ...")
    mockers.mock_print_build.assert_any_call("docker run -it", derived_label)
    mockers.mock_print_tools.assert_any_call(mockers.client.value.replace('"', ""))


def test_docker_build_check_enable(mocker, restore_pwd):
    args = MockArgs(
        check_only=False,
        clean=False,
        enable={"vscode": os_path.expandvars("$HEKIT_PATH/docker/Dockerfile.vscode")},
    )
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""

    main()
    assert 1 == mockers.mock_create_tar_gz.call_count
    assert 1 == mockers.mock_change_dir.call_count
    assert 1 == mockers.mock_mkdir.call_count
    mockers.mock_print_build.assert_any_call("BUILDING", "BASE", "DOCKERFILE ...")
    mockers.mock_print_build.assert_any_call("BUILDING", "TOOLKIT", "DOCKERFILE ...")
    mockers.mock_print_build.assert_any_call("BUILDING", "VSCODE", "DOCKERFILE ...")
    mockers.mock_print_build.assert_any_call(
        "Then to open vscode navigate to <ip addr>:<port> in your chosen browser"
    )
    mockers.mock_print_tools.assert_any_call(mockers.client.value.replace('"', ""))


def test_docker_build_check_only(mocker, restore_pwd):
    args = MockArgs(check_only=True, clean=False, enable=None)
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert 0 == mockers.mock_create_tar_gz.call_count
    assert 0 == mockers.mock_change_dir.call_count
    assert 0 == mockers.mock_mkdir.call_count
    mockers.mock_print_build.assert_any_call("CHECKING IN-DOCKER CONNECTIVITY ...")
    mockers.mock_print_tools.assert_any_call(
        "[CONTAINER]", mockers.client.log.decode("utf-8"), end=""
    )
    mockers.mock_print_tools.assert_any_call("[CONTAINER]", "\n", end="")
    assert exc_info.value.code == 0


def test_docker_build_clean(mocker, restore_pwd):
    args = MockArgs(check_only=False, clean=True, enable=None)
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""

    with pytest.raises(SystemExit) as exc_info:
        main()
    assert 0 == mockers.mock_create_tar_gz.call_count
    assert 0 == mockers.mock_change_dir.call_count
    assert 0 == mockers.mock_mkdir.call_count
    mockers.mock_print_build.assert_any_call("Staging area deleted")
    assert exc_info.value.code == 0


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, check_only, clean, enable):
        self.tests_path = Path(__file__).resolve().parent
        self.check_only = check_only
        self.clean = clean
        self.enable = enable
        self.config = f"{self.tests_path}/input_files/default.config"
        self.hekit_root_dir = self.tests_path.parent
        self.fn = setup_docker
        self.id = None
        self.version = False
        self.debug = False
        self.y = True


class Mockers:
    def __init__(self, mocker):
        self.client = MockClient()
        # Mocking command line args
        self.mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
        # Mocking objects from docker_build
        self.mock_input = mocker.patch("kit.commands.docker_build.input")
        self.mock_input.return_value = "a"
        self.mock_print_build = mocker.patch("kit.commands.docker_build.print")
        self.mock_create_tar_gz = mocker.patch(
            "kit.commands.docker_build.create_tar_gz_file"
        )
        self.mock_change_dir = mocker.patch(
            "kit.commands.docker_build.change_directory_to"
        )
        self.mock_mkdir = mocker.patch.object(Path, "mkdir")
        # Mocking objects from docker_tools
        self.mock_from_env = mocker.patch("kit.utils.docker_tools.docker_from_env")
        self.mock_from_env.return_value = self.client
        self.mock_print_tools = mocker.patch("kit.utils.docker_tools.print")


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
