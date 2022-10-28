# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from kit.commands.install import install_components, get_recipe_arg_dict


def test_install_components_all_unskipped(mocker, args, unskipped_components):
    """All components are installed because skip flag is equal to False"""
    mock_component = mocker.patch("kit.commands.install.components_to_build_from")
    mock_component.return_value = unskipped_components
    mock_print = mocker.patch("kit.utils.component_builder.print")

    install_components(args)
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )
    mock_print.assert_called_with(
        "[HEKIT]", "component/instance:", "component_test/instance_test"
    )
    assert 3 == mock_print.call_count


def test_install_components_all_skipped(mocker, args, skipped_components):
    """All components are skipped because skip flag is equal to True"""
    mock_component = mocker.patch("kit.commands.install.components_to_build_from")
    mock_component.return_value = skipped_components
    mock_print = mocker.patch("kit.utils.component_builder.print")

    install_components(args)
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )
    mock_print.assert_called_with(
        "[HEKIT]", "Skipping component/instance:", "component_test/instance_test"
    )
    assert 6 == mock_print.call_count


def test_install_components_one_unskipped(mocker, args, one_unskipped_component):
    """Only two of three components are skipped when skip flag is equal to False"""
    mock_component = mocker.patch("kit.commands.install.components_to_build_from")
    mock_component.return_value = one_unskipped_component
    mock_print = mocker.patch("kit.utils.component_builder.print")

    install_components(args)
    mock_component.assert_called_once()
    mock_component.assert_called_with(
        args.recipe_file, args.config.repo_location, args.recipe_arg
    )
    mock_print.assert_called_with(
        "[HEKIT]", "Skipping component/instance:", "component_test/instance_test"
    )
    assert 5 == mock_print.call_count


def test_get_recipe_arg_dict_correct_format():
    act_arg = "key1=value1, key2=value2, key3=value3"
    exc_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}

    act_dict = get_recipe_arg_dict(act_arg)
    assert exc_dict == act_dict


def test_get_recipe_arg_dict_duplicated_key():
    act_arg = "key1=value1, key1=value2, key3=value3"
    exc_dict = {"key1": "value2", "key3": "value3"}

    act_dict = get_recipe_arg_dict(act_arg)
    assert exc_dict == act_dict


def test_get_recipe_arg_dict_wrong_format():
    act_arg = "key1=value1, key1=value2, key3"
    with pytest.raises(ValueError) as execinfo:
        get_recipe_arg_dict(act_arg)
    assert "Wrong format for ['key3']. Expected key=value" == str(execinfo.value)


def test_get_recipe_arg_dict_missing_comma():
    act_arg = "key1=value1 key2=value2, key3=value3"
    with pytest.raises(ValueError) as execinfo:
        get_recipe_arg_dict(act_arg)
    assert (
        "Wrong format for ['key1', 'value1key2', 'value2']. Expected key=value"
        == str(execinfo.value)
    )


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.config = f"{self.tests_path}/input_files/default.config"
        self.recipe_file = "file_test"
        self.upto_stage = "install"
        self.force = False
        self.recipe_arg = {"version": "1.2.3"}


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

    def reset_stage_info_file(self, stage):
        pass


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
