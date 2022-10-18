# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from sys import stderr
from pathlib import Path
from kit.hekit import main
from kit.commands.init import init_hekit, create_default_workspace


def test_init_hekit_create_config_file(mocker, tmp_path):
    mockers = Mockers(mocker, tmp_path, default_config_flag=True)
    mockers.create_tmp_config_file()
    # Create a new config file
    main()
    mockers.mock_print.assert_any_call(f"{tmp_path}/.hekit/default.config created")
    mockers.mock_print.assert_any_call(f"source {mockers.filepath}")
    # Try to create a new config file, but it exists
    main()
    mockers.mock_print.assert_any_call(
        f"{tmp_path}/.hekit/default.config file already exists"
    )
    mockers.mock_print.assert_any_call(f"source {mockers.filepath}")


def test_init_hekit_rcfile_unmodified(mocker, tmp_path):
    mockers = Mockers(mocker, tmp_path, default_config_flag=True)
    mockers.mock_input.return_value = "n"
    mockers.create_tmp_config_file()
    # Create a new config file
    main()
    mockers.mock_print.assert_any_call(
        "Please execute the following actions manually:\n"
        f"1. Open the file {tmp_path}/.mybashfile\n"
        "2. Add the lines shown in the previous message"
        f"\n3. Source your shell config file with: source {tmp_path}/.mybashfile"
    )


def test_init_hekit_rcfile_FileNotFoundError(mocker, tmp_path):
    mockers = Mockers(mocker, tmp_path, default_config_flag=False)
    with pytest.raises(SystemExit) as exc_info:
        main()
    mockers.mock_hekit_print.assert_called_with(
        "Error while running subcommand\n",
        f"FileNotFoundError(PosixPath('{tmp_path}/.mybashfile'))",
        file=stderr,
    )
    assert 0 != exc_info.value.code


"""Utilities used by the tests"""


class Mockers:
    def __init__(self, mocker, tmp_path, default_config_flag):
        self.filepath = tmp_path / ".mybashfile"
        self.mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
        self.mock_parse_cmdline.return_value = MockArgs(default_config_flag), ""
        self.mock_create_default_workspace = mocker.patch(
            "kit.commands.init.create_default_workspace",
            return_value=create_default_workspace(tmp_path),
        )
        self.mock_get_rc_file = mocker.patch("kit.commands.init.get_rc_file")
        self.mock_get_rc_file.return_value = self.filepath
        self.mock_print = mocker.patch("kit.commands.init.print")
        self.mock_hekit_print = mocker.patch("kit.hekit.print")
        self.mock_input = mocker.patch("kit.commands.init.input", return_value="y")

    def create_tmp_config_file(self):
        with self.filepath.open("w") as f:
            f.write("test\n")


class MockArgs:
    def __init__(self, default_config_flag):
        self.tests_path = Path(__file__).resolve().parent
        self.config = f"{self.tests_path}/input_files/default.config"
        self.default_config = default_config_flag
        self.fn = init_hekit
        self.hekit_root_dir = Path("/home")
        self.version = False
        self.debug = False
