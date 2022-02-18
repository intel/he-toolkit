import pytest
from os import getcwd, chdir

from .context import hekit, config, command_list, command_remove, command_install
from hekit import main
from config import load_config
from command_list import list_components
from command_remove import remove_components
from command_install import install_components

# Due to install command changes current directory,
# the other commands need to restore the current path
cwd_test = getcwd()


def test_command_install_execution(mocker, args_install):
    """Arrange"""
    """chain_run function is executed because skip is equal to False"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_install, ""
    mock_print = mocker.patch("command_install.print")

    """Act"""
    main()

    """Assert"""
    arg1 = f"{args_install.component}/{args_install.instance}"
    mock_print.assert_any_call(arg1)


def test_command_list_execution(mocker, args_list, restore_pwd):
    """Arrange"""
    """chain_run function is executed because skip is equal to False"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_list, ""
    mock_print = mocker.patch("command_list.print")

    """Act"""
    main()

    """Assert"""
    width = 10
    arg1 = f"{args_list.component:{width}} {args_list.instance:{width}}"
    arg234 = f"{'success':{width}}"
    mock_print.assert_any_call(arg1, arg234, arg234, arg234)


def test_command_remove_execution(mocker, args_remove, restore_pwd):
    """Arrange"""
    """chain_run function is executed because skip is equal to False"""
    mock_parse_cmdline = mocker.patch("hekit.parse_cmdline")
    mock_parse_cmdline.return_value = args_remove, ""
    mock_print = mocker.patch("command_remove.print")

    """Act"""
    main()

    """Assert"""
    arg1 = f"Instance '{args_remove.instance}' of component '{args_remove.component}' successfully removed"
    mock_print.assert_any_call(arg1)


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, fn):
        self.version = False
        self.component = "hexl"
        self.instance = "1.2.3"
        self.config = "tests/config/default.config"
        self.install_file = "tests/config/test.toml"
        self.fn = fn


@pytest.fixture
def args_install():
    return MockArgs(install_components)


@pytest.fixture
def args_list():
    return MockArgs(list_components)


@pytest.fixture
def args_remove():
    return MockArgs(remove_components)


@pytest.fixture
def restore_pwd():
    global cwd_test
    chdir(cwd_test)
