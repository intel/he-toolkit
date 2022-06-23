# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import tests.context
from kit.utils.component_builder import (
    chain_run,
    run,
    BuildError,
    components_to_build_from,
    ComponentBuilder,
)


def test_chain_run_all_success(mocker, funcs_success):
    try:
        """Act"""
        chain_run(funcs_success)

        """Assert"""
        assert True
    except Exception as exc:
        """Assert"""
        assert False, f"'chain_run' raised an exception {exc}"


def test_chain_run_all_failure(mocker, funcs_failure):
    """Arrange"""
    exp_error, funcs = funcs_failure
    exp_value = f"Function '{funcs[0].__name__}' failed to execute external process"

    """Act"""
    with pytest.raises(BuildError) as exc_info:
        chain_run(funcs)

    """Assert"""
    assert exc_info.value.args[0] == exp_value
    assert exc_info.value.error == exp_error


def test_run_success(mocker, cmd_and_args, Popen_success):
    """Arrange"""
    exp_status, exp_code = Popen_success
    mock_Popen = mocker.patch("kit.utils.component_builder.Popen")
    mock_proc = mock_Popen.return_value.__enter__.return_value
    mock_proc.returncode = exp_code

    """Act"""
    act_status, act_code = run(cmd_and_args)

    """Assert"""
    assert act_status == exp_status
    assert act_code == exp_code
    mock_Popen.assert_called_once()


def test_run_failure(mocker, cmd_and_args, Popen_failure):
    """Arrange"""
    exp_status, exp_code = Popen_failure
    mock_Popen = mocker.patch("kit.utils.component_builder.Popen")
    mock_proc = mock_Popen.return_value.__enter__.return_value
    mock_proc.returncode = exp_code

    """Act"""
    act_status, act_code = run(cmd_and_args)

    """Assert"""
    assert act_status == exp_status
    assert act_code == exp_code
    mock_Popen.assert_called_once()


def test_run_without_arguments(mocker):
    """Arrange"""
    mock_Popen = mocker.patch("kit.utils.component_builder.Popen")

    """Act"""
    act_status, act_code = run("")

    """Assert"""
    assert act_status == True
    assert act_code == 0
    mock_Popen.assert_not_called()


def test_components_to_build_from_(mocker, specs_data):
    """Arrange"""
    exp_filename, exp_repo, exp_recipe_arg, exp_spec = specs_data
    mock_Spec = mocker.patch("kit.utils.component_builder.Spec.from_toml_file")
    mock_Spec.return_value = exp_spec
    mock_ComponentBuilder = mocker.patch.object(ComponentBuilder, "__init__")
    mock_ComponentBuilder.return_value = None

    """Act"""
    act_result = components_to_build_from(exp_filename, exp_repo, exp_recipe_arg)

    """Assert"""
    for result in act_result:
        assert type(result) == ComponentBuilder
    assert mock_ComponentBuilder.call_count == 3
    mock_Spec.assert_called_with(exp_filename, exp_repo, exp_recipe_arg)


"""Utilities used by the tests"""


@pytest.fixture
def funcs_success():
    def func_success():
        return (True, 0)

    return [func_success, func_success, func_success]


@pytest.fixture
def funcs_failure():
    exp_error = 56

    def func_failire():
        return (False, exp_error)

    return exp_error, [func_failire]


@pytest.fixture
def cmd_and_args():
    return "git clone https://github.com/test/test.git --branch v1.1.1"


@pytest.fixture
def Popen_success():
    return True, 0


@pytest.fixture
def Popen_failure():
    return False, 1


@pytest.fixture
def specs_data():
    filename = "hexl"
    repo = "/home/test/components"
    recipe_arg = {"version": "2.3.1"}

    class Spec:
        def __init__(self):
            self.component = filename
            self._instance_spec = {
                "skip": False,
                "version": "1.2.3",
                "name": "1.2.3",
                "fetch": "test",
                "init_fetch_dir": "test",
                "init_build_dir": "test",
                "init_install_dir": "test",
                "pre-build": "test",
                "build": "test",
                "install": "test",
                "export_install_dir": "test",
                "export_cmake": "test",
            }
            self.repo_location = repo

    return filename, repo, recipe_arg, [Spec(), Spec(), Spec()]
