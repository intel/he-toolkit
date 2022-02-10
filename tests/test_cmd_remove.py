# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import patch

from .context import command_remove
from command_remove import remove_components


class MockArgs:
    class Config:
        def __init__(self):
            self.repo_location = "test_location "

    def __init__(self):
        self.config = MockArgs.Config()
        self.instance = "test_instance"
        self.component = "component"


def test_remove_components():
    with patch("command_remove.rmtree") as mock_rmtree:
        with patch("command_remove.print") as mock_print:
            mockargs = MockArgs()
            remove_components(mockargs)

        mock_print.assert_called_once()
        text = f"Instance '{mockargs.instance}' of component '{mockargs.component}' successfully removed"
        mock_print.assert_called_with(text)
    mock_rmtree.assert_called_once()
    path = f"{mockargs.config.repo_location}/{mockargs.component}/{mockargs.instance}"
    mock_rmtree.assert_called_with(path)


def test_remove_components_2():
    with patch("command_remove.rmtree") as mock_rmtree:
        mock_rmtree.side_effect = FileNotFoundError

        with patch("command_remove.print") as mock_print:
            mockargs = MockArgs()
            remove_components(mockargs)

        mock_print.assert_called_once()
        text = f"Instance '{mockargs.instance}' of component '{mockargs.component}' not found."
        mock_print.assert_called_with("Nothing to remove", text)
    mock_rmtree.assert_called_once()
    path = f"{mockargs.config.repo_location}/{mockargs.component}/{mockargs.instance}"
    mock_rmtree.assert_called_with(path)
