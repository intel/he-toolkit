# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import PropertyMock
import pytest
from sys import stderr
from pathlib import Path
from kit.hekit import main
from kit.utils.constants import Constants
from kit.commands.init import init_hekit, create_default_workspace


def test_init_hekit_create_config_file(mocker, tmp_path):
    """Verify that the SW creates the folder and files after executing
    the init command. Also, verify that the SW reports an error
    when re-executing the init command because the files exist"""
    mockers = Mockers(mocker, tmp_path, default_config_flag=True)
    mockers.create_tmp_config_file()
    # Create a new config file
    main()
    mockers.mock_print.assert_any_call(f"{tmp_path}/.hekit/default.config created")
    mockers.mock_print.assert_any_call(
        "Please source your shell config file as follows\n" f"source {mockers.filepath}"
    )
    # Try to create a new config file, but it exists
    main()
    mockers.mock_print.assert_any_call(
        f"{tmp_path}/.hekit/default.config file already exists"
    )
    mockers.mock_print.assert_any_call(
        "Please source your shell config file as follows\n" f"source {mockers.filepath}"
    )


def test_init_hekit_rcfile_unmodified(mocker, tmp_path):
    """Verify that the SW shows the actions to modify the
    rc file when the user selects manual modification"""
    mockers = Mockers(mocker, tmp_path, default_config_flag=True)
    mockers.mock_input.return_value = "n"
    mockers.create_tmp_config_file()
    # Create a new config file
    main()
    mockers.mock_print.assert_any_call(
        "Please execute the following actions manually:\n"
        f"1. Open the file {tmp_path}/.mybashfile in an editor\n"
        "2. Add the lines shown in the previous message"
        f"\n3. Source your shell config file with: source {tmp_path}/.mybashfile"
    )


def test_init_hekit_bash_shell(mocker, tmp_path):
    """Verify that the SW shows the actions to modify the
    rc file when the user selects manual modification"""
    mockers = Mockers(mocker, tmp_path, default_config_flag=True)
    mockers.mock_input.return_value = "n"
    mockers.create_tmp_config_file()

    main()
    mockers.mock_input.assert_any_call(
        f"The hekit init command will update the file {tmp_path}/.mybashfile to append the following lines:\n\n"
        "# >>> hekit start >>>\n"
        "export HEKITPATH=/myhome/user/he-toolkit\n"
        "PATH=$PATH:$HEKITPATH\n"
        'if [ -n "$(type -p register-python-argcomplete)" ]; then\n'
        '  eval "$(register-python-argcomplete hekit)"\n'
        "fi\n"
        "# <<<  hekit end  <<<\n\n"
        "NOTE: a backup file will be created before updating it.\n"
        "Do you want to continue with this action? (y/n) "
    )


def test_init_hekit_zsh_shell(mocker, tmp_path):
    """Verify that the SW shows the actions to modify the
    rc file when the user selects manual modification"""
    mockers = Mockers(mocker, tmp_path, default_config_flag=True, active_shell="zsh")
    mockers.mock_input.return_value = "n"
    mockers.create_tmp_config_file()

    main()
    mockers.mock_input.assert_any_call(
        f"The hekit init command will update the file {tmp_path}/.mybashfile to append the following lines:\n\n"
        "# >>> hekit start >>>\n"
        "export HEKITPATH=/myhome/user/he-toolkit\n"
        "PATH=$PATH:$HEKITPATH\n"
        "autoload -U bashcompinit\n"
        "bashcompinit\n"
        'if [ -n "$(type -p register-python-argcomplete)" ]; then\n'
        '  eval "$(register-python-argcomplete hekit)"\n'
        "fi\n"
        "# <<<  hekit end  <<<\n\n"
        "NOTE: a backup file will be created before updating it.\n"
        "Do you want to continue with this action? (y/n) "
    )


def test_init_hekit_rcfile_FileNotFoundError(mocker, tmp_path):
    """Verify that the SW throws an error when executing
    init command and the rc file does not exist"""
    mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
    mock_parse_cmdline.return_value = MockArgs(default_config_flag=False), ""
    mock_hekit_print = mocker.patch("kit.hekit.print")
    mock_exists = mocker.patch.dict(
        "kit.commands.init.environment", {"SHELL": "myshell"}
    )

    with pytest.raises(SystemExit) as exc_info:
        main()
    mock_hekit_print.assert_called_with(
        "Error while running subcommand\n",
        "ValueError(\"Unknown shell 'myshell'\")",
        file=stderr,
    )
    assert 0 != exc_info.value.code


"""Utilities used by the tests"""


class Mockers:
    def __init__(self, mocker, tmp_path, default_config_flag, active_shell="bash"):
        self.filepath = tmp_path / ".mybashfile"
        self.mock_parse_cmdline = mocker.patch("kit.hekit.parse_cmdline")
        self.mock_parse_cmdline.return_value = MockArgs(default_config_flag), ""
        self.mock_create_default_workspace = mocker.patch(
            "kit.commands.init.create_default_workspace",
            return_value=create_default_workspace(tmp_path),
        )
        self.mock_get_rc_file = mocker.patch("kit.commands.init.get_shell_rc_file")
        self.mock_get_rc_file.return_value = active_shell, self.filepath
        self.mock_print = mocker.patch("kit.commands.init.print")
        self.mock_hekit_print = mocker.patch("kit.hekit.print")
        self.mock_input = mocker.patch("kit.commands.init.input", return_value="y")
        self.const_hekit_path = mocker.patch.object(
            Constants, "HEKIT_ROOT_DIR", new_callable=PropertyMock
        )
        self.const_hekit_path.return_value = Path("/myhome/user/he-toolkit")

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
