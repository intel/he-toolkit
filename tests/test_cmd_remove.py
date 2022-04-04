# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from .context import command_remove
from command_remove import remove_components


def test_remove_instance_no_error(mocker, args):
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


def test_remove_component_no_error(mocker, args):
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


@pytest.fixture
def args():
    return MockArgs()
