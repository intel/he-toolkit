# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from kit.commands.list_cmd import list_components, RepoProperties, _SEP_SPACES


def test_get_repo_properties_max_width(mocker):
    exp_comps = ["1234567", "123", "123456789"]
    exp_inst1 = ["123"]
    exp_inst2 = ["1", "1234567890123456"]
    exp_inst3 = ["123456"]
    mock_list_dirs = mocker.patch("kit.commands.list_cmd.list_dirs")
    mock_list_dirs.side_effect = [exp_comps, exp_inst1, exp_inst2, exp_inst3]
    exp_repo_structure = {
        exp_comps[0]: exp_inst1,
        exp_comps[1]: exp_inst2,
        exp_comps[2]: exp_inst3,
    }
    exp_width_comp = 9 + _SEP_SPACES
    exp_width_inst = 16 + _SEP_SPACES

    act_props = RepoProperties("")
    assert act_props.structure == exp_repo_structure
    assert act_props.width_comp == exp_width_comp
    assert act_props.width_inst == exp_width_inst


def test_get_repo_properties_without_instances(mocker):
    exp_comps = ["12345678901234567890"]
    exp_inst1 = []
    mock_list_dirs = mocker.patch("kit.commands.list_cmd.list_dirs")
    mock_list_dirs.side_effect = [exp_comps, exp_inst1]
    exp_repo_structure = {exp_comps[0]: exp_inst1}
    exp_width_comp = 20 + _SEP_SPACES
    exp_width_inst = 8 + _SEP_SPACES

    act_props = RepoProperties("")
    assert act_props.structure == exp_repo_structure
    assert act_props.width_comp == exp_width_comp
    assert act_props.width_inst == exp_width_inst


def test_get_repo_properties_without_components(mocker):
    exp_comps = []
    exp_inst1 = []
    mock_list_dirs = mocker.patch("kit.commands.list_cmd.list_dirs")
    mock_list_dirs.side_effect = [exp_comps, exp_inst1]
    exp_repo_structure = {}
    exp_width_comp = 9 + _SEP_SPACES
    exp_width_inst = 8 + _SEP_SPACES

    act_props = RepoProperties("")
    assert act_props.structure == exp_repo_structure
    assert act_props.width_comp == exp_width_comp
    assert act_props.width_inst == exp_width_inst


def test_list_components_several_correct_items(
    mocker, args, tree_directory, all_actions_success
):
    """list_cmd_dirs function is called several times, first
    it returns the libraries, then the version of each one"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=tree_directory)
    """load function returns success as status of the all the actions"""
    mock_load = mocker.patch(
        "kit.commands.list_cmd.load_toml", return_value=all_actions_success
    )
    mock_print = mocker.patch("kit.commands.list_cmd.print")

    list_components(args)
    assert 8 == mock_walk.call_count
    assert 8 == mock_load.call_count
    assert 9 == mock_print.call_count


def test_list_components_incorrect_fetch(
    mocker, args, lib_directory, fetch_failure, name_version_lib
):
    """list_dirs function is called two times, first
    it returns a library and then its version"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=lib_directory)
    """load function returns failure as status of fetch"""
    mock_load = mocker.patch(
        "kit.commands.list_cmd.load_toml", return_value=fetch_failure
    )
    """print functions reports the failure for fetch"""
    mock_print = mocker.patch("kit.commands.list_cmd.print")
    exp_lib, exp_version = name_version_lib
    arg1, arg2, arg3, arg4 = get_print_args(exp_lib, exp_version, fetch_failure)

    list_components(args)
    assert 2 == mock_walk.call_count
    assert 1 == mock_load.call_count
    assert 2 == mock_print.call_count
    mock_print.assert_called_with(arg1, arg2, arg3, arg4)


def test_list_components_incorrect_build(
    mocker, args, lib_directory, build_failure, name_version_lib
):
    """list_dirs function is called two times, first
    it returns a library and then its version"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=lib_directory)
    """load function returns failure as status of build"""
    mock_load = mocker.patch(
        "kit.commands.list_cmd.load_toml", return_value=build_failure
    )
    """print functions reports the failure for build"""
    mock_print = mocker.patch("kit.commands.list_cmd.print")
    exp_lib, exp_version = name_version_lib
    arg1, arg2, arg3, arg4 = get_print_args(exp_lib, exp_version, build_failure)

    list_components(args)
    assert 2 == mock_walk.call_count
    assert 1 == mock_load.call_count
    assert 2 == mock_print.call_count
    mock_print.assert_called_with(arg1, arg2, arg3, arg4)


def test_list_components_incorrect_install(
    mocker, args, lib_directory, install_failure, name_version_lib
):
    """list_dirs function is called two times, first
    it returns a library and then its version"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=lib_directory)
    """load function returns failure as status of install"""
    mock_load = mocker.patch(
        "kit.commands.list_cmd.load_toml", return_value=install_failure
    )
    """print functions reports the failure for install"""
    mock_print = mocker.patch("kit.commands.list_cmd.print")
    exp_lib, exp_version = name_version_lib
    arg1, arg2, arg3, arg4 = get_print_args(exp_lib, exp_version, install_failure)

    list_components(args)
    assert 2 == mock_walk.call_count
    assert 1 == mock_load.call_count
    assert 2 == mock_print.call_count
    mock_print.assert_called_with(arg1, arg2, arg3, arg4)


def test_list_components_without_version(mocker, without_version_directory, args):
    """list_dirs function is called two times, first
    it returns a library and then it tries its version"""
    mock_walk = mocker.patch(
        "kit.utils.files.walk", side_effect=without_version_directory
    )
    mock_load = mocker.patch("kit.commands.list_cmd.load_toml")
    mock_print = mocker.patch("kit.commands.list_cmd.print")

    list_components(args)
    assert 2 == mock_walk.call_count
    assert 1 == mock_print.call_count
    mock_load.assert_not_called()


def test_list_components_without_libraries(mocker, args, without_lib_directory):
    """list_dirs function is called once but
    there are not libraries"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=without_lib_directory)
    mock_load = mocker.patch("kit.commands.list_cmd.load_toml")
    mock_print = mocker.patch("kit.commands.list_cmd.print")

    list_components(args)
    assert 1 == mock_walk.call_count
    assert 1 == mock_print.call_count
    mock_load.assert_not_called()


def test_list_components_StopIteration_exception(mocker, args):
    """list_dirs function triggers a StopIteration exception
    and returns an empty list"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=StopIteration)
    mock_load = mocker.patch("kit.commands.list_cmd.load_toml")
    mock_print = mocker.patch("kit.commands.list_cmd.print")

    list_components(args)
    assert 1 == mock_walk.call_count
    assert 1 == mock_print.call_count
    mock_load.assert_not_called()


def test_list_components_FileNotFoundError_exception(
    mocker, args, lib_directory, name_version_lib
):
    exp_lib, exp_version = name_version_lib
    """list_dirs function is called two times, first
    it returns the library then its version"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=lib_directory)
    """ load triggers an FileNotFoundError exception"""
    mock_load = mocker.patch(
        "kit.commands.list_cmd.load_toml", side_effect=FileNotFoundError
    )
    """print functions reports the exception"""
    mock_print = mocker.patch("kit.commands.list_cmd.print")

    list_components(args)
    info_filepath = f"{args.config.repo_location}/{exp_lib}/{exp_version}/hekit.info"
    arg1, arg2, arg3, arg4, arg5 = util_print_file_error_args(
        exp_lib, exp_version, info_filepath
    )
    mock_print.assert_called_with(arg1, arg2, arg3, arg4, arg5)
    assert 2 == mock_walk.call_count
    assert 1 == mock_load.call_count
    assert 2 == mock_print.call_count


def test_list_components_KeyError_exception(
    mocker, args, lib_directory, name_version_lib
):
    """list_dirs function is called two times, first
    it returns a library and then its version"""
    mock_walk = mocker.patch("kit.utils.files.walk", side_effect=lib_directory)
    """load function triggers a KeyError exception"""
    mock_load = mocker.patch("kit.commands.list_cmd.load_toml", side_effect=KeyError)
    """print functions reports the exception"""
    mock_print = mocker.patch("kit.commands.list_cmd.print")
    exp_lib, exp_version = name_version_lib
    arg1, arg2, arg3, arg4, arg5 = util_print_key_error_args(exp_lib, exp_version, "")

    list_components(args)
    mock_walk.assert_called()
    assert 2 == mock_walk.call_count
    assert 1 == mock_load.call_count
    assert 2 == mock_print.call_count
    mock_print.assert_called_with(arg1, arg2, arg3, arg4, arg5)


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.config = f"{self.tests_path}/input_files/default.config"


@pytest.fixture
def args():
    return MockArgs()


@pytest.fixture
def tree_directory():
    return [
        iter(
            [("", ["test1", "test2", "test3", "test4", "test5", "test6", "test7"], [])]
        ),
        iter([("", ["v3.1.0"], [])]),
        iter([("", ["v2.2.1"], [])]),
        iter([("", ["1.2.1", "1.2.3"], [])]),
        iter([("", ["11.5.1"], [])]),
        iter([("", ["v1.11.6"], [])]),
        iter([("", ["v3.7.2"], [])]),
        iter([("", ["v1.4.5"], [])]),
    ]


@pytest.fixture
def name_version_lib():
    return "hexl", "v3.1.0"


@pytest.fixture
def lib_directory(name_version_lib):
    exp_lib, exp_version = name_version_lib
    return [iter([("", [exp_lib], [])]), iter([("", [exp_version], [])])]


@pytest.fixture
def without_version_directory(name_version_lib):
    exp_lib, _ = name_version_lib
    return [iter([("", [exp_lib], [])]), iter([("", [], [])])]


@pytest.fixture
def without_lib_directory():
    return [iter([("", [], [])])]


@pytest.fixture
def all_actions_success():
    return {"status": {"fetch": "success", "build": "success", "install": "success"}}


@pytest.fixture
def fetch_failure():
    return {"status": {"fetch": "failure", "build": "success", "install": "success"}}


@pytest.fixture
def build_failure():
    return {"status": {"fetch": "success", "build": "failure", "install": "success"}}


@pytest.fixture
def install_failure():
    return {"status": {"fetch": "success", "build": "success", "install": "failure"}}


def get_width_and_header(comp_name, comp_inst, separation_spaces=_SEP_SPACES):
    width = 10

    width_comp = (
        len(comp_name) if len(comp_name) > len("component") else len("component")
    )
    width_comp += separation_spaces
    width_inst = len(comp_inst) if len(comp_inst) > len("instance") else len("instance")
    width_inst += separation_spaces
    return width, f"{comp_name:{width_comp}} {comp_inst:{width_inst}}"


def get_print_args(comp_name, comp_inst, info_file):
    width, column1 = get_width_and_header(comp_name, comp_inst)
    column2 = f"{info_file['status']['fetch']:{width}}"
    column3 = f"{info_file['status']['build']:{width}}"
    column4 = f"{info_file['status']['install']:{width}}"

    return column1, column2, column3, column4


def util_print_file_error_args(comp_name, comp_inst, info_filepath):
    width, column1 = get_width_and_header(comp_name, comp_inst)
    columns234 = f"{'unknown':{width}}"
    column5 = f"file '{info_filepath}' not found"

    return column1, columns234, columns234, columns234, column5


def util_print_key_error_args(comp_name, comp_inst, emsg):
    width, column1 = get_width_and_header(comp_name, comp_inst)
    columns234 = f"{'unknown':{width}}"
    column5 = f"key {emsg} not found"

    return column1, columns234, columns234, columns234, column5
