# Copyright (C) 2020-2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from unittest.mock import patch

from .context import command_list
from command_list import list_components


class MockArgs:
    class Config:
        def __init__(self):
            self.repo_location = "test"

    def __init__(self):
        self.config = MockArgs.Config()


def test_list_components_several_correct_items():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called several times, first
        it returns the libraries, then the version of each one"""
        mock_walk.side_effect = [
            iter(
                [
                    (
                        "",
                        ["test1", "test2", "test3", "test4", "test5", "test6", "test7"],
                        [],
                    )
                ]
            ),
            iter([("", ["v3.1.0"], [])]),
            iter([("", ["v2.2.1"], [])]),
            iter([("", ["1.2.1", "1.2.3"], [])]),
            iter([("", ["11.5.1"], [])]),
            iter([("", ["v1.11.6"], [])]),
            iter([("", ["v3.7.2"], [])]),
            iter([("", ["v1.4.5"], [])]),
        ]

        with patch("command_list.load") as mock_load:
            """Returns success as status of the all the actions"""
            mock_load.return_value = {
                "status": {"fetch": "success", "build": "success", "install": "success"}
            }
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_called()
        assert 8 == mock_load.call_count
    mock_walk.assert_called()
    assert 8 == mock_walk.call_count


def test_list_components_incorrect_fetch():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called two times, first
        it returns a library and then its version"""
        mock_walk.side_effect = [
            iter([("", ["hexl"], [])]),
            iter([("", ["v3.1.0"], [])]),
        ]

        with patch("command_list.load") as mock_load:
            """Returns failure as status of fetch"""
            mock_load.return_value = {
                "status": {"fetch": "failure", "build": "", "install": ""}
            }
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_called_once()
    mock_walk.assert_called()
    assert 2 == mock_walk.call_count


def test_list_components_incorrect_build():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called two times, first
        it returns a library and then its version"""
        mock_walk.side_effect = [
            iter([("", ["hexl"], [])]),
            iter([("", ["v3.1.0"], [])]),
        ]

        with patch("command_list.load") as mock_load:
            """Returns failure as status of build"""
            mock_load.return_value = {
                "status": {"fetch": "success", "build": "failure", "install": ""}
            }
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_called_once()
    mock_walk.assert_called()
    assert 2 == mock_walk.call_count


def test_list_components_incorrect_install():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called two times, first
        it returns a library and then its version"""
        mock_walk.side_effect = [
            iter([("", ["hexl"], [])]),
            iter([("", ["v3.1.0"], [])]),
        ]

        with patch("command_list.load") as mock_load:
            """Returns failure as status of install"""
            mock_load.return_value = {
                "status": {"fetch": "success", "build": "success", "install": "failure"}
            }
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_called_once()
    mock_walk.assert_called()
    assert 2 == mock_walk.call_count


def test_list_components_without_version():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called two times, first
        it returns a library and then its version"""
        mock_walk.side_effect = [iter([("", ["hexl"], [])]), iter([("", [], [])])]

        with patch("command_list.load") as mock_load:
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_not_called()
    mock_walk.assert_called()
    assert 2 == mock_walk.call_count


def test_list_components_without_libraries():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called once but
        there are not libraries"""
        mock_walk.side_effect = [iter([("", [], [])])]

        with patch("command_list.load") as mock_load:
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_not_called()
    mock_walk.assert_called_once()


def test_list_components_FileNotFoundError_exception():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called two times, first
        it returns the library then its version"""
        mock_walk.side_effect = [
            iter([("", ["hexl"], [])]),
            iter([("", ["v3.1.0"], [])]),
        ]

        with patch("command_list.load") as mock_load:
            """Triggers an FileNotFoundError exception for load"""
            mock_load.side_effect = FileNotFoundError
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_called_once()
    mock_walk.assert_called()
    assert 2 == mock_walk.call_count


def test_list_components_KeyError_exception():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function is called two times, first
        it returns a library and then its version"""
        mock_walk.side_effect = [
            iter([("", ["hexl"], [])]),
            iter([("", ["v3.1.0"], [])]),
        ]

        with patch("command_list.load") as mock_load:
            """Triggers a KeyError exception for load"""
            mock_load.return_value = {"status": {"fetch": "success"}}

            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_called_once()
    mock_walk.assert_called()
    assert 2 == mock_walk.call_count


def test_list_components_StopIteration_exception():
    with patch("command_list.walk") as mock_walk:
        """list_dirs function triggers a StopIteration exception
        and returns an empty list"""
        mock_walk.side_effect = StopIteration

        with patch("command_list.load") as mock_load:
            mockargs = MockArgs()
            list_components(mockargs)

        mock_load.assert_not_called()
    mock_walk.assert_called_once()
