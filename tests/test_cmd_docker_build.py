# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from kit.utils.docker_tools import DockerException
from kit.utils.constants import Constants
from kit.commands.docker_build import (
    copyfiles,
    create_buildargs,
    print_preamble,
    filter_file_list,
    create_tar_gz_file,
    setup_docker,
)


def test_copyfiles_execution(mocker):
    """Arrange"""
    files = ["file1", "file2", "file3"]
    src_dir = "source"
    dst_dir = "destiny"
    exp_arg1 = Path(src_dir) / files[2]
    exp_arg2 = Path(dst_dir) / files[2]

    mock_copyfile = mocker.patch("kit.commands.docker_build.copyfile")

    """Act"""
    copyfiles(files, src_dir, dst_dir)

    """Assert"""
    assert 3 == mock_copyfile.call_count
    mock_copyfile.assert_called_with(exp_arg1, exp_arg2)


def test_create_buildargs_with_ID(mocker):
    """Arrange"""
    act_env = {"key": "value"}
    act_ID = 23

    """Act"""
    exp_value = create_buildargs(act_env, act_ID)

    """Assert"""
    assert exp_value["UID"] == str(act_ID)
    assert exp_value["GID"] == str(act_ID)
    assert exp_value["UNAME"] == Constants.user
    assert exp_value["key"] == "value"
    assert exp_value["TOOLKIT_BASE_IMAGE"] == Constants.base_label
    assert exp_value["VSCODE_BASE_IMAGE"] == Constants.toolkit_label


def test_create_buildargs_Darwin(mocker):
    """Arrange"""
    act_env = {"key": "value"}
    act_ID = 0
    exp_ID = "1000"
    mock_os_name = mocker.patch("kit.commands.docker_build.os_name")
    mock_os_name.return_value = "Darwin"

    """Act"""
    exp_value = create_buildargs(act_env, act_ID)

    """Assert"""
    assert exp_value["UID"] == str(exp_ID)
    assert exp_value["GID"] == str(exp_ID)
    assert exp_value["UNAME"] == Constants.user
    assert exp_value["key"] == "value"
    assert exp_value["TOOLKIT_BASE_IMAGE"] == Constants.base_label
    assert exp_value["VSCODE_BASE_IMAGE"] == Constants.toolkit_label


def test_create_buildargs_other(mocker):
    """Arrange"""
    act_env = {"key": "value"}
    act_ID = 0
    exp_uid, exp_id = 1234, 5678
    mock_os_name = mocker.patch("kit.commands.docker_build.os_name")
    mock_os_name.return_value = "other"
    mock_getuid = mocker.patch("kit.commands.docker_build.getuid")
    mock_getuid.return_value = exp_uid
    mock_getgid = mocker.patch("kit.commands.docker_build.getgid")
    mock_getgid.return_value = exp_id

    """Act"""
    exp_value = create_buildargs(act_env, act_ID)

    """Assert"""
    assert exp_value["UID"] == str(exp_uid)
    assert exp_value["GID"] == str(exp_id)
    assert exp_value["UNAME"] == Constants.user
    assert exp_value["key"] == "value"
    assert exp_value["TOOLKIT_BASE_IMAGE"] == Constants.base_label
    assert exp_value["VSCODE_BASE_IMAGE"] == Constants.toolkit_label


def test_print_preamble_normal_execution(mocker):
    """Arrange"""
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_exit = mocker.patch("kit.commands.docker_build.sys_exit")
    mock_input = mocker.patch("kit.commands.docker_build.input")
    mock_input.return_value = "a"

    """Act"""
    print_preamble()

    """Assert"""
    mock_print.assert_called_once()
    mock_exit.assert_not_called()


def test_print_preamble_KeyboardInterrupt(mocker):
    """Arrange"""
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_exit = mocker.patch("kit.commands.docker_build.sys_exit")
    mock_input = mocker.patch("kit.commands.docker_build.input")
    mock_input.side_effect = KeyboardInterrupt()

    """Act"""
    print_preamble()

    """Assert"""
    assert 2 == mock_print.call_count
    mock_exit.assert_called_once_with(1)


def test_filter_file_list_execution(mocker):
    """Arrange"""
    exp_file = "CorrectFile"
    file_list = iter(["#comment", "       ", exp_file, "#comment 2", ""])

    """Act"""
    exp_value = filter_file_list(file_list)

    """Assert"""
    assert next(exp_value) == exp_file


def test_create_tar_gz_file_execution(mocker):
    """Arrange"""
    toolkit_tar_gz = Path("/home/myFile.tar.gz")
    archived_files = "/home/test"
    ROOT = "/home/he-toolkit"
    exp_files = "file"

    mock_exists = mocker.patch.object(Path, "exists")
    mock_exists.return_value = False
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_open = mocker.patch("kit.commands.docker_build.open")
    mock_filter = mocker.patch("kit.commands.docker_build.filter_file_list")
    mock_filter.return_value = exp_files
    mock_compress = mocker.patch("kit.commands.docker_build.archive_and_compress")

    """Act"""
    create_tar_gz_file(toolkit_tar_gz, archived_files, ROOT)

    """Assert"""
    mock_print.assert_called_once_with("MAKING TOOLKIT.TAR.GZ ...")
    mock_open.assert_called_once_with(archived_files, encoding="utf-8")
    mock_compress.assert_called_with(toolkit_tar_gz, exp_files, root=ROOT)


def test_create_tar_gz_file_FileExistsError(mocker):
    """Arrange"""
    toolkit_tar_gz = Path("/home/myFile.tar.gz")
    archived_files = "/home/test"
    ROOT = "/home/he-toolkit"
    exp_files = "file"

    mock_exists = mocker.patch.object(Path, "exists")
    mock_exists.return_value = False
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_open = mocker.patch("kit.commands.docker_build.open")
    mock_filter = mocker.patch("kit.commands.docker_build.filter_file_list")
    mock_filter.return_value = exp_files
    mock_compress = mocker.patch("kit.commands.docker_build.archive_and_compress")
    mock_compress.side_effect = FileExistsError()

    """Act"""
    create_tar_gz_file(toolkit_tar_gz, archived_files, ROOT)

    """Assert"""
    assert 2 == mock_print.call_count
    mock_open.assert_called_once_with(archived_files, encoding="utf-8")
    mock_compress.assert_called_with(toolkit_tar_gz, exp_files, root=ROOT)


def test_create_tar_gz_file_File_Exists(mocker):
    """Arrange"""
    toolkit_tar_gz = Path("/home/myFile.tar.gz")
    archived_files = "/home/test"
    ROOT = "/home/he-toolkit"

    mock_exists = mocker.patch.object(Path, "exists")
    mock_exists.return_value = True
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_open = mocker.patch("kit.commands.docker_build.open")
    mock_filter = mocker.patch("kit.commands.docker_build.filter_file_list")
    mock_compress = mocker.patch("kit.commands.docker_build.archive_and_compress")

    """Act"""
    create_tar_gz_file(toolkit_tar_gz, archived_files, ROOT)

    """Assert"""
    mock_print.assert_not_called()
    mock_open.assert_not_called()
    mock_filter.assert_not_called()
    mock_compress.assert_not_called()


def test_setup_docker_clean(mocker):
    """Arrange"""
    args = MockArgs(clean=True, y=True, check_only=True, enable="vscode")
    mock_rmtree = mocker.patch("kit.commands.docker_build.rmtree")
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_print_preamble = mocker.patch("kit.commands.docker_build.print_preamble")
    mock_DockerTools = mocker.patch("kit.commands.docker_build.DockerTools")

    """Act"""
    with pytest.raises(SystemExit) as exc_info:
        setup_docker(args)

    """Assert"""
    mock_rmtree.assert_called_with(Path(args.hekit_root_dir) / "__staging__")
    mock_print.assert_called_with("Staging area deleted")
    mock_print_preamble.assert_not_called()
    mock_DockerTools.assert_not_called()
    assert exc_info.value.code == 0


def test_setup_docker_docker_error(mocker):
    """Arrange"""
    args = MockArgs(clean=False, y=True, check_only=True, enable="vscode")
    mock_rmtree = mocker.patch("kit.commands.docker_build.rmtree")
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_print_preamble = mocker.patch("kit.commands.docker_build.print_preamble")
    mock_DockerTools = mocker.patch("kit.commands.docker_build.DockerTools")
    mock_DockerTools.side_effect = DockerException()

    """Act"""
    with pytest.raises(SystemExit) as exc_info:
        setup_docker(args)

    """Assert"""
    mock_rmtree.assert_not_called()
    mock_print_preamble.assert_called()
    mock_DockerTools.assert_called()
    assert exc_info.value.code == 1


def test_setup_docker_check_only(mocker):
    """Arrange"""
    args = MockArgs(clean=False, y=False, check_only=True, enable="vscode")
    doc_build = MockDockerTools()
    mock_rmtree = mocker.patch("kit.commands.docker_build.rmtree")
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_print_preamble = mocker.patch("kit.commands.docker_build.print_preamble")
    mock_DockerTools = mocker.patch("kit.commands.docker_build.DockerTools")
    mock_DockerTools.return_value = doc_build

    """Act"""
    with pytest.raises(SystemExit) as exc_info:
        setup_docker(args)

    """Assert"""
    mock_rmtree.assert_not_called()
    mock_print_preamble.assert_not_called()
    mock_DockerTools.assert_called()
    mock_print.assert_called_with("CHECKING IN-DOCKER CONNECTIVITY ...")
    assert exc_info.value.code == 0


def test_setup_docker_vscode(mocker):
    """Arrange"""
    args = MockArgs(clean=False, y=False, check_only=False, enable="vscode")
    doc_build = MockDockerTools()
    mock_rmtree = mocker.patch("kit.commands.docker_build.rmtree")
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_print_preamble = mocker.patch("kit.commands.docker_build.print_preamble")
    mock_DockerTools = mocker.patch("kit.commands.docker_build.DockerTools")
    mock_DockerTools.return_value = doc_build
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    mock_create_tar_gz = mocker.patch("kit.commands.docker_build.create_tar_gz_file")
    mock_copyfiles = mocker.patch("kit.commands.docker_build.copyfiles")
    mock_change_dir = mocker.patch("kit.commands.docker_build.change_directory_to")

    """Act"""
    setup_docker(args)

    """Assert"""
    mock_rmtree.assert_not_called()
    mock_print_preamble.assert_not_called()
    mock_DockerTools.assert_called()
    mock_mkdir.assert_called()
    mock_create_tar_gz.assert_called()
    mock_copyfiles.assert_called()
    mock_change_dir.assert_called()
    mock_print.assert_any_call("BUILDING VSCODE DOCKERFILE ...")
    mock_print.assert_any_call(
        "Then to open vscode navigate to <ip addr>:<port> in your chosen browser"
    )


def test_setup_docker_build(mocker):
    """Arrange"""
    args = MockArgs(clean=False, y=False, check_only=False, enable=None)
    doc_build = MockDockerTools()

    ROOT = Path(args.hekit_root_dir)
    docker_filepaths = ROOT / "docker"
    staging_path = ROOT / "__staging__"
    toolkit_tar_gz = staging_path / "toolkit.tar.gz"
    archived_files = docker_filepaths / "which-files.txt"
    files_to_copy = ["Dockerfile.base", "Dockerfile.toolkit"]

    mock_rmtree = mocker.patch("kit.commands.docker_build.rmtree")
    mock_print = mocker.patch("kit.commands.docker_build.print")
    mock_print_preamble = mocker.patch("kit.commands.docker_build.print_preamble")
    mock_DockerTools = mocker.patch("kit.commands.docker_build.DockerTools")
    mock_DockerTools.return_value = doc_build
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    mock_create_tar_gz = mocker.patch("kit.commands.docker_build.create_tar_gz_file")
    mock_copyfiles = mocker.patch("kit.commands.docker_build.copyfiles")
    mock_change_dir = mocker.patch("kit.commands.docker_build.change_directory_to")

    """Act"""
    setup_docker(args)

    """Assert"""
    mock_rmtree.assert_not_called()
    mock_print_preamble.assert_not_called()
    mock_DockerTools.assert_called()
    mock_mkdir.assert_called()
    mock_create_tar_gz.assert_called_with(toolkit_tar_gz, archived_files, ROOT)
    mock_copyfiles.assert_called_with(
        files_to_copy, src_dir=docker_filepaths, dst_dir=staging_path
    )
    mock_change_dir.assert_called_with(staging_path)
    mock_print.assert_any_call("Run container with")


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, clean, y, check_only, enable):
        self.hekit_root_dir = "/home"
        self.clean = clean
        self.y = y
        self.check_only = check_only
        self.enable = enable
        self.id = 1
        self.version = "2.0.0"


class MockDockerTools:
    def test_connection(self, environment, scriptpath):
        return True

    def try_build_new_image(self, dockerfile, tag, buildargs):
        return True
