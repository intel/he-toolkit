# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from .context import hekit, command_init
from hekit import main
from command_init import init_hekit


def test_init_hekit_config_file_exists(mocker):
    """Arrange"""
    args = MockArgs()
    rc_file = "~/.mybashfile"
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""
    mockers.mock_get_rc_file.return_value = rc_file
    mockers.mock_same_files.return_value = True
    mockers.mock_exists.side_effect = [True, True]

    """Act"""
    main()

    """Assert"""
    # create_default_config function
    mockers.mock_mkdir.assert_called_once()
    mockers.mock_print.assert_any_call("~/.hekit/default.config file already exists")
    # create_backup function
    mockers.mock_copyfile.assert_called_once()
    mockers.mock_same_files.assert_called_once()
    # init_hekit function
    mockers.mock_remove_from_rc.assert_called_once()
    mockers.mock_append_to_rc.assert_called_once()
    mockers.mock_print.assert_any_call(f"source {rc_file}")


def test_init_hekit_config_file_is_created(mocker):
    """Arrange"""
    args = MockArgs()
    rc_file = "~/.mybashfile"
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""
    mockers.mock_get_rc_file.return_value = rc_file
    mockers.mock_same_files.return_value = True
    mockers.mock_exists.side_effect = [False, True]

    """Act"""
    main()

    """Assert"""
    # create_default_config function
    mockers.mock_mkdir.assert_called_once()
    mockers.mock_open.assert_called_once()
    mockers.mock_print.assert_any_call("~/.hekit/default.config created")
    # create_backup function
    mockers.mock_copyfile.assert_called_once()
    mockers.mock_same_files.assert_called_once()
    # init_hekit function
    mockers.mock_remove_from_rc.assert_called_once()
    mockers.mock_append_to_rc.assert_called_once()
    mockers.mock_print.assert_any_call(f"source {rc_file}")


def test_init_hekit_config_FileNotFoundError_from_get_expanded_path(mocker):
    """Arrange"""
    args = MockArgs()
    rc_file = "~/.mybashfile"
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""
    mockers.mock_get_rc_file.return_value = rc_file
    mockers.mock_same_files.return_value = True
    mockers.mock_exists.side_effect = [False, False]

    """Act"""
    with pytest.raises(FileNotFoundError) as exc_info:
        main()

    """Assert"""
    # create_default_config function
    mockers.mock_mkdir.assert_called_once()
    mockers.mock_open.assert_called_once()
    mockers.mock_print.assert_any_call("~/.hekit/default.config created")
    # create_backup function
    mockers.mock_copyfile.assert_not_called()
    mockers.mock_same_files.assert_not_called()
    # init_hekit function
    mockers.mock_remove_from_rc.assert_not_called()
    mockers.mock_append_to_rc.assert_not_called()


def test_init_hekit_ValueError_from_create_backup(mocker):
    """Arrange"""
    args = MockArgs()
    rc_file = "~/.mybashfile"
    mockers = Mockers(mocker)
    mockers.mock_parse_cmdline.return_value = args, ""
    mockers.mock_get_rc_file.return_value = rc_file
    mockers.mock_same_files.return_value = False
    mockers.mock_exists.side_effect = [True, True]

    """Act"""
    with pytest.raises(ValueError) as exc_info:
        main()

    """Assert"""
    # create_default_config function
    mockers.mock_mkdir.assert_called_once()
    mockers.mock_print.assert_any_call("~/.hekit/default.config file already exists")
    # create_backup function
    mockers.mock_copyfile.assert_called_once()
    mockers.mock_same_files.assert_called_once()
    # init_hekit function
    mockers.mock_remove_from_rc.assert_not_called()
    mockers.mock_append_to_rc.assert_not_called()


"""Utilities used by the tests"""


class Mockers:
    def __init__(self, mocker):
        # mocking functions for Path Objects
        self.mock_mkdir = mocker.patch.object(Path, "mkdir")
        self.mock_open = mocker.patch.object(Path, "open")
        # mocking included functions
        self.mock_print = mocker.patch("command_init.print")
        self.mock_copyfile = mocker.patch("command_init.copyfile")
        self.mock_same_files = mocker.patch("command_init.same_files")
        # mocking internal functions
        self.mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
        self.mock_get_rc_file = mocker.patch("command_init.get_rc_file")
        self.mock_exists = mocker.patch("command_init.file_exists")
        self.mock_remove_from_rc = mocker.patch("command_init.remove_from_rc")
        self.mock_append_to_rc = mocker.patch("command_init.append_to_rc")


class MockArgs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.config = f"{self.tests_path}/input_files/default.config"
        self.default_config = True
        self.fn = init_hekit
        self.hekit_root_dir = Path("/home")
        self.version = False
