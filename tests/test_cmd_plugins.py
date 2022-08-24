# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from kit.utils.constants import PluginsConfig, PluginState
from kit.commands.plugin import list_plugins


def test_list_plugins_all(mocker):
    """Verify it prints all plugins"""
    args = MockArgs()
    mockers = Mockers(mocker)

    list_plugins(args)
    assert 3 == mockers.mock_print.call_count
    mockers.mock_print.assert_any_call("plugin2    disabled  ")
    mockers.mock_print.assert_any_call("plugin1    enabled   ")


def test_list_plugins_ENABLE(mocker):
    """Verify it prints only enabled plugins"""
    args = MockArgs()
    args.state = PluginState.ENABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    # assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with("plugin1    enabled   ")


def test_list_plugins_DISABLE(mocker):
    """Verify it prints only disabled plugins"""
    args = MockArgs()
    args.state = PluginState.DISABLE
    mockers = Mockers(mocker)

    list_plugins(args)
    # assert 2 == mockers.mock_print.call_count
    mockers.mock_print.assert_called_with("plugin2    disabled  ")


"""Utilities used by the tests"""


def geet_fake_dict():
    return {"plugin1": PluginState.ENABLE, "plugin2": PluginState.DISABLE}


class MockArgs:
    def __init__(self):
        self.state = "all"
        self.plugin = "plugin1"
        self.force = False
        self.all = False


class Mockers:
    def __init__(self, mocker):
        self.mock_print = mocker.patch("kit.commands.plugin.print")
        self.mock_plugin_dict = mocker.patch("kit.commands.plugin.get_plugin_dict")
        self.mock_plugin_dict.return_value = geet_fake_dict()
