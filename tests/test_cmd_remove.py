# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from kit.commands.remove import remove_components


def test_remove_instance_of_component_with_many_instances(mocker, args):
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=["v2.3.2"])
    text = f"Instance '{args.instance}' of component '{args.component}' successfully removed"

    remove_components(args)
    path = f"{args.config.repo_location}/{args.component}/{args.instance}"
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_called_once()


def test_remove_instance_of_component_with_single_instance(mocker, args):
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    text = f"Instance '{args.instance}' of component '{args.component}' successfully removed"

    remove_components(args)
    path = f"{args.config.repo_location}/{args.component}"
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    assert 2 == mock_rmtree.call_count
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_called_once()


def test_remove_all_instances_answer_yes(mocker, args):
    args.instance = None
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    mock_input = mocker.patch("kit.commands.remove.input", return_value="y")
    text = f"All instances of component '{args.component}' successfully removed"

    remove_components(args)
    path = f"{args.config.repo_location}/{args.component}"
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_instances_answer_no(mocker, args):
    args.instance = None
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    mock_input = mocker.patch("kit.commands.remove.input", return_value="n")

    remove_components(args)
    mock_print.assert_not_called()
    mock_rmtree.assert_not_called()
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_components_answer_yes(mocker, args):
    args.all = True
    args.instance = ""
    args.component = ""
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    mock_input = mocker.patch("kit.commands.remove.input", return_value="y")
    text = f"All components successfully removed"

    remove_components(args)
    path = f"{args.config.repo_location}"
    mock_print.assert_called_once()
    mock_print.assert_called_with(text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_components_answer_no(mocker, args):
    args.all = True
    args.instance = ""
    args.component = ""
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    mock_input = mocker.patch("kit.commands.remove.input", return_value="n")

    remove_components(args)
    mock_print.assert_not_called()
    mock_rmtree.assert_not_called()
    mock_listdir.assert_not_called()
    mock_input.assert_called_once()


def test_remove_all_ValueError_exception(mocker, args):
    args.all = True
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    mock_input = mocker.patch("kit.commands.remove.input", return_value="n")

    with pytest.raises(ValueError) as execinfo:
        remove_components(args)
    assert (
        str(execinfo.value)
        == "Flag '--all' cannot be used when specifying a component or instance"
    )


def test_remove_component_ValueError_exception(mocker, args):
    args.component = ""
    mock_rmtree = mocker.patch("kit.commands.remove.rmtree")
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    mock_input = mocker.patch("kit.commands.remove.input", return_value="n")

    with pytest.raises(ValueError) as execinfo:
        remove_components(args)
    assert (
        str(execinfo.value)
        == "A component or flag '--all' should be specified as argument"
    )


def test_remove_components_FileNotFoundError_exception(mocker, args):
    mock_rmtree = mocker.patch(
        "kit.commands.remove.rmtree", side_effect=FileNotFoundError
    )
    mock_print = mocker.patch("kit.commands.remove.print")
    mock_listdir = mocker.patch("kit.commands.remove.listdir", return_value=[])
    text = f"Instance '{args.instance}' of component '{args.component}' not found."

    remove_components(args)
    path = f"{args.config.repo_location}/{args.component}/{args.instance}"
    mock_print.assert_called_once()
    mock_print.assert_called_with("Nothing to remove", text)
    mock_rmtree.assert_called_once()
    mock_rmtree.assert_called_with(path)
    mock_listdir.assert_not_called()


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self):
        self.tests_path = Path(__file__).resolve().parent
        self.config = f"{self.tests_path}/input_files/default.config"
        self.instance = "test_instance"
        self.component = "component"
        self.all = False
        self.y = True


@pytest.fixture
def args():
    return MockArgs()
