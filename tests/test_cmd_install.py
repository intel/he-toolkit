# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import patch

from .context import command_install, spec, component_builder
from command_install import install_components
from spec import Spec
from component_builder import ComponentBuilder


class MockArgs:
    class Config:
        def __init__(self):
            self.repo_location = "location_test"

    def __init__(self):
        self.config = MockArgs.Config()
        self.install_file = "file_test"


class MockComponent:
    def __init__(self, skip, result):
        self._skip = skip
        self._result = result

    def skip(self):
        return self._skip

    def component_name(self):
        return "component_test"

    def instance_name(self):
        return "instance_test"

    def setup(self):
        return self._result

    def fetch(self):
        return self._result

    def build(self):
        return self._result

    def install(self):
        return self._result


def test_install_components_all_unskipped():
    with patch("command_install.components_to_build_from") as mock_component:
        """chain_run function is executed because skip is equal to False"""
        exp_skip = False
        exp_result = True, 0
        exp_comp1 = MockComponent(exp_skip, exp_result)
        exp_comp2 = MockComponent(exp_skip, exp_result)
        exp_comp3 = MockComponent(exp_skip, exp_result)
        mock_component.return_value = [exp_comp1, exp_comp2, exp_comp3]

        with patch("command_install.chain_run") as mock_chain_run:
            mockargs = MockArgs()
            install_components(mockargs)

        mock_chain_run.assert_called()
        assert 3 == mock_chain_run.call_count
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        mockargs.install_file, mockargs.config.repo_location
    )


def test_install_components_all_skipped():
    with patch("command_install.components_to_build_from") as mock_component:
        """chain_run function is not executed because skip is equal to True"""
        exp_skip = True
        exp_result = False, 568
        exp_comp1 = MockComponent(exp_skip, exp_result)
        exp_comp2 = MockComponent(exp_skip, exp_result)
        exp_comp3 = MockComponent(exp_skip, exp_result)
        mock_component.return_value = [exp_comp1, exp_comp2, exp_comp3]

        with patch("command_install.chain_run") as mock_chain_run:
            mockargs = MockArgs()
            install_components(mockargs)

        mock_chain_run.assert_not_called()
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        mockargs.install_file, mockargs.config.repo_location
    )


def test_install_components_some_skipped():
    with patch("command_install.components_to_build_from") as mock_component:
        """chain_run function is executed once when skip is equal to True"""
        exp_result = True, 0
        exp_comp1 = MockComponent(True, exp_result)
        exp_comp2 = MockComponent(False, exp_result)
        exp_comp3 = MockComponent(True, exp_result)
        mock_component.return_value = [exp_comp1, exp_comp2, exp_comp3]

        with patch("command_install.chain_run") as mock_chain_run:
            mockargs = MockArgs()
            install_components(mockargs)

        mock_chain_run.assert_called_once()
        mock_chain_run.assert_called_with(
            [exp_comp2.setup, exp_comp2.fetch, exp_comp2.build, exp_comp2.install]
        )
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        mockargs.install_file, mockargs.config.repo_location
    )
