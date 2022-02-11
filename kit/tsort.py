# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0


class CycleError(Exception):
    """Error for indicating a cycle found in an DAG"""


def tsort(G: dict):
    """Topological sort of graph G"""
    # Following Python 3.9 TopologicalSorter.static_order();
    # The dict values are the nodes pointing to the keys.

    def dfs(node, path):
        """Recursive generator. Depth first search."""
        if len(path) > 1 and path[0] == path[-1]:
            raise CycleError(f"cycle:{path}")
        if node in visited:
            return
        visited.add(node)
        try:
            for next_node in G[node]:
                yield from dfs(next_node, [*path, next_node])
        except KeyError:
            pass
        yield node

    visited = set()

    for node in G.keys():
        yield from dfs(node, [node])
