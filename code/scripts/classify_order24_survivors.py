#!/usr/bin/env python3
"""Classify the nine order-24 Delta=3 edge-critical survivors.

For each survivor we decide whether it is a *vertex-blowup* of the unique
order-22 survivor (via the inverse contractible-triangle deflation), and for the
one blowup-irreducible survivor we compute its even-order snark-completions.

Result:
  - 8 of 9 (all girth 3) are vertex-blowups of the order-22 survivor;
  - G5 (girth 5, triangle-free) is blowup-irreducible ("primitive").

Reproducible: run from codes/critical_graph_search/.
"""

from __future__ import annotations

import gzip
import itertools
import json
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1] / "results"


def all_triangles(graph: nx.Graph) -> list[tuple[int, int, int]]:
    """List every triangle in deterministic vertex order."""
    return [
        (a, b, c)
        for a, b, c in itertools.combinations(sorted(graph.nodes()), 3)
        if graph.has_edge(a, b) and graph.has_edge(a, c) and graph.has_edge(b, c)
    ]


def contractible_triangle_data(
    graph: nx.Graph,
    triangle: tuple[int, int, int],
) -> tuple[tuple[int, int, int], list[int]] | None:
    """Return the external-neighbor profile when a triangle can be deflated."""
    triangle_set = set(triangle)
    external_neighbors: list[int] = []
    profile: list[int] = []
    for vertex in triangle:
        outside = [neighbor for neighbor in graph.neighbors(vertex) if neighbor not in triangle_set]
        if len(outside) > 1:
            return None
        profile.append(len(outside))
        external_neighbors.extend(outside)
    if len(external_neighbors) != len(set(external_neighbors)):
        return None
    return tuple(sorted(profile, reverse=True)), external_neighbors


def contract_triangle(
    graph: nx.Graph,
    triangle: tuple[int, int, int],
) -> tuple[nx.Graph, tuple[int, int, int], list[int]] | None:
    """Deflate a contractible triangle to one vertex."""
    info = contractible_triangle_data(graph, triangle)
    if info is None:
        return None
    profile, external_neighbors = info
    contracted = graph.copy()
    contracted.add_node("contracted")
    for neighbor in external_neighbors:
        contracted.add_edge("contracted", neighbor)
    contracted.remove_nodes_from(triangle)
    contracted = nx.convert_node_labels_to_integers(contracted)
    return contracted, profile, external_neighbors


def load_order22() -> nx.Graph:
    data = json.load(gzip.open(RESULTS / "order_22_delta_3.json.gz"))
    return nx.from_graph6_bytes(data["survivors"][0]["graph6"].encode())


def load_order24() -> list[dict]:
    data = json.load(gzip.open(RESULTS / "order_24_delta_3.json.gz"))
    return data["survivors"]


def is_class2(graph: nx.Graph) -> bool:
    """True iff graph is NOT Delta-edge-colourable (class 2). Exact backtracking."""
    delta = max(d for _, d in graph.degree())
    edges = list(graph.edges())
    ne = len(edges)
    adj = [[] for _ in range(ne)]
    for a in range(ne):
        for b in range(a + 1, ne):
            if set(edges[a]) & set(edges[b]):
                adj[a].append(b)
                adj[b].append(a)
    colour = [-1] * ne

    def backtrack(i: int) -> bool:
        if i == ne:
            return True
        used = {colour[j] for j in adj[i] if colour[j] != -1}
        for c in range(delta):
            if c not in used:
                colour[i] = c
                if backtrack(i + 1):
                    return True
                colour[i] = -1
        return False

    return not backtrack(0)


def deflates_to(graph: nx.Graph, target: nx.Graph):
    """Return a contractible triangle whose contraction is isomorphic to target, or None."""
    for tri in all_triangles(graph):
        if contractible_triangle_data(graph, tri) is None:
            continue
        res = contract_triangle(graph, tri)
        if res is None:
            continue
        contracted = res[0]
        if contracted.number_of_nodes() == target.number_of_nodes() and nx.is_isomorphic(
            contracted, target
        ):
            return tri
    return None


def matching_completions(graph: nx.Graph, deg2: list[int]):
    """Perfect-matching completion: add a perfect matching on the four degree-2 vertices
    (2 edges, no new vertices) -> cubic. Report each pairing's (cubic, girth, class2)."""
    out = []
    a = deg2[0]
    for b in deg2[1:]:
        rest = [x for x in deg2 if x not in (a, b)]
        H = graph.copy()
        if H.has_edge(a, b) or H.has_edge(rest[0], rest[1]):
            out.append(((a, b), (rest[0], rest[1]), None))
            continue
        H.add_edge(a, b)
        H.add_edge(rest[0], rest[1])
        cubic = all(d == 3 for _, d in H.degree())
        out.append(
            (
                (a, b),
                (rest[0], rest[1]),
                {"cubic": cubic, "girth": nx.girth(H), "class2": is_class2(H) if cubic else None},
            )
        )
    return out


def main() -> None:
    g22 = load_order22()
    survivors = load_order24()

    print(f"order-22 base: n={g22.number_of_nodes()} m={g22.number_of_edges()} girth={nx.girth(g22)}\n")
    blowups, primitives = [], []
    for i, s in enumerate(survivors, start=1):
        graph = nx.from_graph6_bytes(s["graph6"].encode())
        girth = nx.girth(graph)
        tri = deflates_to(graph, g22)
        label = f"G{i}"
        if tri is not None:
            blowups.append(label)
            print(f"{label}: girth={girth} alpha={s['alpha']} -> BLOWUP of order-22 (contract {tri})")
        else:
            primitives.append(label)
            print(f"{label}: girth={girth} alpha={s['alpha']} -> PRIMITIVE (blowup-irreducible)")
            deg2 = sorted(v for v in graph if graph.degree(v) == 2)
            print(f"    degree-2 vertices: {deg2}; triangle count: {len(all_triangles(graph))}")
            for p1, p2, info in matching_completions(graph, deg2):
                print(f"    matching {{{p1[0]},{p1[1]}}},{{{p2[0]},{p2[1]}}} completion: {info}")

    print(f"\nblowups of order-22 ({len(blowups)}): {blowups}")
    print(f"primitive ({len(primitives)}): {primitives}")


if __name__ == "__main__":
    main()
