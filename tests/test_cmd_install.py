# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from .context import command_install
from command_install import install_components, _stages


def test_install_components_all_unskipped(mocker, args, unskipped_components):
    """Arrange"""
    """chain_run function is executed because skip is equal to False"""
    mock_component = mocker.patch("command_install.components_to_build_from")
    mock_component.return_value = unskipped_components
    mock_chain_run = mocker.patch("command_install.chain_run")

    """Act"""
    install_components(args)

    """Assert"""
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )
    assert 3 == mock_chain_run.call_count


def test_install_components_all_skipped(mocker, args, skipped_components):
    """Arrange"""
    """chain_run function is not executed because skip is equal to True"""
    mock_component = mocker.patch("command_install.components_to_build_from")
    mock_component.return_value = skipped_components
    mock_chain_run = mocker.patch("command_install.chain_run")

    """Act"""
    install_components(args)

    """Assert"""
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )
    mock_chain_run.assert_not_called()


def test_install_components_one_unskipped(mocker, args, one_unskipped_component):
    """Arrange"""
    """chain_run function is executed once when skip is equal to False"""
    mock_component = mocker.patch("command_install.components_to_build_from")
    mock_component.return_value = one_unskipped_component
    mock_chain_run = mocker.patch("command_install.chain_run")

    """Act"""
    install_components(args)

    """Assert"""
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )
    mock_chain_run.assert_called_once()


def test_stages_fetch(mocker, unskipped_components):
    """Arrange"""
    comp = unskipped_components[0]
    upto_stage = "fetch"

    """Act"""
    the_stages = _stages(upto_stage)
    act_result = the_stages(comp)

    """Assert"""
    assert next(act_result) == comp.setup
    assert next(act_result) == comp.fetch


def test_stages_build(mocker, unskipped_components):
    """Arrange"""
    comp = unskipped_components[1]
    upto_stage = "build"

    """Act"""
    the_stages = _stages(upto_stage)
    act_result = the_stages(comp)

    """Assert"""
    assert next(act_result) == comp.setup
    assert next(act_result) == comp.fetch
    assert next(act_result) == comp.build


def test_stages_install(mocker, unskipped_components):
    """Arrange"""
    comp = unskipped_components[2]
    upto_stage = "install"

    """Act"""
    the_stages = _stages(upto_stage)
    act_result = the_stages(comp)

    """Assert"""
    assert next(act_result) == comp.setup
    assert next(act_result) == comp.fetch
    assert next(act_result) == comp.build
    assert next(act_result) == comp.install


"""Utilities used by the tests"""


class MockArgs:
    class Config:
        def __init__(self):
            self.repo_location = "location_test"

    def __init__(self):
        self.config = MockArgs.Config()
        self.recipe_file = "file_test"
        self.upto_stage = "install"
        self.recipe_arg = "version=1.2.3"


class MockComponent:
    def __init__(self, skip):
        self._skip = skip
        self._result = (True, 0)

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


@pytest.fixture
def args():
    return MockArgs()


@pytest.fixture
def unskipped_components():
    return [MockComponent(False), MockComponent(False), MockComponent(False)]


@pytest.fixture
def skipped_components():
    return [MockComponent(True), MockComponent(True), MockComponent(True)]


@pytest.fixture
def one_unskipped_component():
    return [MockComponent(True), MockComponent(False), MockComponent(True)]
