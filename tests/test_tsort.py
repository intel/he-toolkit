# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from .context import tsort
from tsort import tsort, CycleError


def test_tsort_of_DAG():
    """Golden path tests. Can it sort given a DAG."""
    # The dict values are the nodes pointing to the keys.
    G = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
    # Only two acceptable sorts here
    # ABCD or ACBD
    tsorted_nodes = "".join(tsort(G))
    assert tsorted_nodes == "ABCD" or tsorted_nodes == "ACBD"

    # Graph from https://en.wikipedia.org/wiki/Topological_sorting
    # hash(int) == int in python unlike strings used above.
    G = {2: {11}, 9: {8, 11}, 10: {3, 11}, 11: {5, 7}, 8: {7, 3}}
    assert tuple(tsort(G)) == (5, 7, 11, 2, 3, 8, 9, 10)


def test_tsort_handles_cycle():
    """Should through an CycleError exception if a cycle is detected."""
    # Graph with a cycle
    G = {15: {6}, 2: {11, 15}, 6: {2}}
    with pytest.raises(CycleError):
        tuple(tsort(G))
