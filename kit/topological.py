#!/usr/bin/env python3


def tsort(G: dict):
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        try:
            for next_node in G[node]:
                yield from dfs(next_node)
        except KeyError:
            pass
        yield node

    visited = set()

    for node in G.keys():
        yield from dfs(node)


if __name__ == "__main__":

    # Following Python 3.9 TopologicalSorter.static_order();
    # The dict values are the nodes pointing to the keys.
    G = {"D": {"B", "C"}, "C": {"A"}, "B": {"A"}}
    # Only two acceptable sorts here
    # ABCD or ACBD

    G = {2: {11}, 9: {8, 11}, 10: {3, 11}, 11: {5, 7}, 8: {7, 3}}
    print(*tsort(G))
