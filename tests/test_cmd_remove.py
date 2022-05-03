# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from .context import command_remove
from command_remove import remove_components


def test_remove_instance_of_component_with_many_instances(mocker, args):
    """Arrange"""
    mock_rmtree = mocker.patch("command_remove.rmtree")
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=["v2.3.2"])
    text = f"Instance '{args.instance}' of component '{args.component}' successfully removed"
    path = f"{args.config.repo_location}/{args.component}/{args.instance}"

    """Act"""
    remove_components(args)

    """Assert"""
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_called_once()


def test_remove_instance_of_component_with_single_instance(mocker, args):
    """Arrange"""
    mock_rmtree = mocker.patch("command_remove.rmtree")
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=[])
    text = f"Instance '{args.instance}' of component '{args.component}' successfully removed"
    path = f"{args.config.repo_location}/{args.component}"

    """Act"""
    remove_components(args)

    """Assert"""
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    assert 2 == mock_rmtree.call_count
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_called_once()


def test_remove_all_instances_answer_yes(mocker, args):
    """Arrange"""
    args.instance = None
    mock_rmtree = mocker.patch("command_remove.rmtree")
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=[])
    mock_input = mocker.patch("command_remove.input", return_value="y")
    text = f"All instances of component '{args.component}' successfully removed"
    path = f"{args.config.repo_location}/{args.component}"

    """Act"""
    remove_components(args)

    """Assert"""
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_instances_answer_no(mocker, args):
    """Arrange"""
    args.instance = None
    mock_rmtree = mocker.patch("command_remove.rmtree")
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=[])
    mock_input = mocker.patch("command_remove.input", return_value="n")

    """Act"""
    remove_components(args)

    """Assert"""
    mock_print.assert_not_called()
    mock_rmtree.assert_not_called()
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_components_answer_yes(mocker, args):
    """Arrange"""
    args.all = True
    args.instance = ""
    args.component = ""
    mock_rmtree = mocker.patch("command_remove.rmtree")
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=[])
    mock_input = mocker.patch("command_remove.input", return_value="y")
    text = f"All components successfully removed"
    path = f"{args.config.repo_location}"

    """Act"""
    remove_components(args)

    """Assert"""
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_components_answer_no(mocker, args):
    """Arrange"""
    args.all = True
    args.instance = ""
    args.component = ""
    mock_rmtree = mocker.patch("command_remove.rmtree")
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=[])
    mock_input = mocker.patch("command_remove.input", return_value="n")

    """Act"""
    remove_components(args)

    """Assert"""
    mock_print.assert_not_called()
    mock_rmtree.assert_not_called()
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_ValueError_exception(mocker, args):
    """Arrange"""
    args.all = True
    mock_rmtree = mocker.patch("command_remove.rmtree")
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=[])
    mock_input = mocker.patch("command_remove.input", return_value="n")

    """Act"""
    with pytest.raises(ValueError) as execinfo:
        remove_components(args)

    """Assert"""
    assert (
        str(execinfo.value)
        == "Flag '--all' cannot be used after specifying a component or instance"
    )


def test_remove_components_FileNotFoundError_exception(mocker, args):
    """Arrange"""
    mock_rmtree = mocker.patch("command_remove.rmtree", side_effect=FileNotFoundError)
    mock_print = mocker.patch("command_remove.print")
    mock_listdir = mocker.patch("command_remove.listdir", return_value=[])
    text = f"Instance '{args.instance}' of component '{args.component}' not found."
    path = f"{args.config.repo_location}/{args.component}/{args.instance}"

    """Act"""
    remove_components(args)

    """Assert"""
    mock_print.assert_called_once()
    mock_print.assert_called_with("Nothing to remove", text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_not_called()


"""Utilities used by the tests"""


class MockArgs:
    class Config:
        def __init__(self):
            self.repo_location = "test_location "

    def __init__(self):
        self.config = MockArgs.Config()
        self.instance = "test_instance"
        self.component = "component"
        self.all = False


@pytest.fixture
def args():
    return MockArgs()
