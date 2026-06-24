#!/usr/bin/python3
"""Classify nontrivial Delta=3 critical survivors by characterization clauses.

This is a deterministic census post-processor for the characterization table in
the combinatorics paper.  It assumes the input JSON files already contain only
the nontrivial 3-critical survivors in the intended scope.  Every survivor is
classified by the first applicable clause:

1. an independent triangle gives clause (a);
2. otherwise any triangle or any cyclic 2-edge-cut gives clause (b);
3. otherwise a subset-minimal smaller side of a cyclic 3-edge-cut with no
   degree-2 vertex gives clause (c);
4. the remaining cyclically 4-edge-connected / snark-completion cases give
   clause (d) for odd order and clause (e) for even order.

The script writes both machine-readable JSON and a Markdown table, and asserts
that the five categories partition each order's survivor set exactly.
"""

from __future__ import annotations

import argparse
import gzip
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent        # repository root (public data repo)
RESULTS = REPO_ROOT / "results"
REPORTS = REPO_ROOT / "reports"

DEFAULT_ORDERS = [13, 15, 17, 19, 21, 22]
DEFAULT_JSON_OUTPUT = REPORTS / "census_characterization_classification.json"
DEFAULT_MD_OUTPUT = REPORTS / "census_characterization_classification.md"

CATEGORIES = [
  "a_vertex_blowup",
  "b_hajos",
  "c_meredith",
  "d_snark",
  "e_snark",
]


def load_json(path: Path) -> dict[str, Any]:
  if path.suffix == ".gz":
    with gzip.open(path, "rt", encoding="utf-8") as handle:
      return json.load(handle)
  return json.loads(path.read_text(encoding="utf-8"))


def result_path_for_order(order: int) -> Path:
  gz = RESULTS / f"order_{order}_delta_3.json.gz"
  if gz.exists():
    return gz
  return RESULTS / f"order_{order}_delta_3.json"


def graph_from_survivor(order: int, survivor: dict[str, Any]) -> nx.Graph:
  graph = nx.Graph()
  graph.add_nodes_from(range(order))
  graph.add_edges_from((int(u), int(v)) for u, v in survivor["edges"])
  return graph


def edge_tuple(edge: tuple[int, int]) -> tuple[int, int]:
  u, v = int(edge[0]), int(edge[1])
  return (u, v) if u < v else (v, u)


def edge_data(graph: nx.Graph) -> tuple[list[tuple[int, int]], list[list[tuple[int, int]]]]:
  edges = sorted(edge_tuple(edge) for edge in graph.edges())
  adjacency: list[list[tuple[int, int]]] = [[] for _node in graph.nodes()]
  for index, (u, v) in enumerate(edges):
    adjacency[u].append((v, index))
    adjacency[v].append((u, index))
  return edges, adjacency


def all_triangles(graph: nx.Graph) -> list[tuple[int, int, int]]:
  adjacency = {int(node): set(int(nbr) for nbr in graph.neighbors(node)) for node in graph.nodes()}
  triangles: set[tuple[int, int, int]] = set()
  for u, v in graph.edges():
    a, b = int(u), int(v)
    for c in adjacency[a] & adjacency[b]:
      triangles.add(tuple(sorted((a, b, int(c)))))
  return sorted(triangles)


def is_independent_triangle(graph: nx.Graph, triangle: tuple[int, int, int]) -> bool:
  triangle_set = set(triangle)
  for vertex in graph.nodes():
    if vertex in triangle_set:
      continue
    hits = sum(1 for nbr in graph.neighbors(vertex) if nbr in triangle_set)
    if hits > 1:
      return False
  return True


def independent_triangles(graph: nx.Graph, triangles: Iterable[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
  return [triangle for triangle in triangles if is_independent_triangle(graph, triangle)]


def component_data(
  order: int,
  adjacency: list[list[tuple[int, int]]],
  cut_indices: tuple[int, ...],
  stop_after_three: bool = True,
) -> list[tuple[frozenset[int], int]]:
  cut = set(cut_indices)
  seen = [False] * order
  components: list[tuple[frozenset[int], int]] = []
  for start in range(order):
    if seen[start]:
      continue
    queue: deque[int] = deque([start])
    seen[start] = True
    vertices: list[int] = []
    degree_sum = 0
    while queue:
      vertex = queue.popleft()
      vertices.append(vertex)
      for nbr, edge_index in adjacency[vertex]:
        if edge_index in cut:
          continue
        degree_sum += 1
        if seen[nbr]:
          continue
        seen[nbr] = True
        queue.append(nbr)
    components.append((frozenset(vertices), degree_sum // 2))
    if stop_after_three and len(components) > 2:
      return components
  return components


def cyclic_cut_components(
  order: int,
  edges: list[tuple[int, int]],
  adjacency: list[list[tuple[int, int]]],
  cut_indices: tuple[int, ...],
) -> tuple[frozenset[int], frozenset[int]] | None:
  del edges
  components = component_data(order, adjacency, cut_indices)
  if len(components) != 2:
    return None
  (first, first_edges), (second, second_edges) = components
  if first_edges < len(first):
    return None
  if second_edges < len(second):
    return None
  return first, second


def has_cyclic_2_edge_cut(order: int, edges: list[tuple[int, int]], adjacency: list[list[tuple[int, int]]]) -> bool:
  for cut_indices in itertools.combinations(range(len(edges)), 2):
    if cyclic_cut_components(order, edges, adjacency, cut_indices) is not None:
      return True
  return False


def smaller_cyclic_3_cut_sides(
  order: int,
  edges: list[tuple[int, int]],
  adjacency: list[list[tuple[int, int]]],
) -> list[frozenset[int]]:
  sides: list[frozenset[int]] = []
  seen: set[frozenset[int]] = set()
  for cut_indices in itertools.combinations(range(len(edges)), 3):
    components = cyclic_cut_components(order, edges, adjacency, cut_indices)
    if components is None:
      continue
    first, second = components
    if len(first) < len(second):
      candidates = [first]
    elif len(second) < len(first):
      candidates = [second]
    else:
      candidates = [first, second]
    for candidate in candidates:
      if candidate not in seen:
        seen.add(candidate)
        sides.append(candidate)
  return sides


def subset_minimal_sides(sides: list[frozenset[int]]) -> list[frozenset[int]]:
  minimal: list[frozenset[int]] = []
  for side in sorted(sides, key=lambda item: (len(item), sorted(item))):
    if any(other < side for other in sides):
      continue
    minimal.append(side)
  return minimal


def classify_graph(graph: nx.Graph) -> tuple[str, dict[str, Any]]:
  order = graph.number_of_nodes()
  degrees = dict(graph.degree())
  triangles = all_triangles(graph)
  indep_triangles = independent_triangles(graph, triangles)
  if indep_triangles:
    return "a_vertex_blowup", {
      "triangle_count": len(triangles),
      "independent_triangle_count": len(indep_triangles),
      "witness_triangle": list(indep_triangles[0]),
    }
  if triangles:
    return "b_hajos", {
      "triangle_count": len(triangles),
      "independent_triangle_count": 0,
      "witness_triangle": list(triangles[0]),
    }

  edges, adjacency = edge_data(graph)
  if has_cyclic_2_edge_cut(order, edges, adjacency):
    return "b_hajos", {
      "triangle_count": 0,
      "independent_triangle_count": 0,
      "reason": "cyclic_2_edge_cut",
    }

  candidate_sides = smaller_cyclic_3_cut_sides(order, edges, adjacency)
  minimal_sides = subset_minimal_sides(candidate_sides)
  for side in minimal_sides:
    if all(degrees[vertex] == 3 for vertex in side):
      return "c_meredith", {
        "triangle_count": 0,
        "minimal_cyclic_3_cut_side_count": len(minimal_sides),
        "witness_side": sorted(side),
      }

  return ("d_snark" if order % 2 else "e_snark"), {
    "triangle_count": 0,
    "minimal_cyclic_3_cut_side_count": len(minimal_sides),
  }


def classify_order(order: int, sample_limit: int = 3) -> dict[str, Any]:
  path = result_path_for_order(order)
  payload = load_json(path)
  survivors = payload["survivors"]
  declared_order = int(payload["order"])
  if declared_order != order:
    raise ValueError(f"{path}: declared order {declared_order} != requested order {order}")

  counts: Counter[str] = Counter()
  samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
  for index, survivor in enumerate(survivors, start=1):
    graph = graph_from_survivor(order, survivor)
    category, witness = classify_graph(graph)
    counts[category] += 1
    if len(samples[category]) < sample_limit:
      samples[category].append({
        "index": index,
        "graph6": survivor["graph6"],
        "witness": witness,
      })

  survivor_count = int(payload["survivor_count"])
  total_classified = sum(counts[category] for category in CATEGORIES)
  row = {
    "input_path": (str(path.relative_to(REPO_ROOT)) if str(path).startswith(str(REPO_ROOT)) else path.name),
    "survivor_count": survivor_count,
    **{category: int(counts[category]) for category in CATEGORIES},
    "total_classified": int(total_classified),
    "sum_check": total_classified == survivor_count == len(survivors),
    "samples": {category: samples.get(category, []) for category in CATEGORIES},
  }
  if not row["sum_check"]:
    raise AssertionError(
      f"order {order}: classified {total_classified}, survivor_count {survivor_count}, "
      f"loaded {len(survivors)}"
    )
  return row


def write_markdown(report: dict[str, Any], path: Path) -> None:
  lines = [
    "# Census characterization classification",
    "",
    "| Order n | survivors | (a) vertex-blowup | (b) Hajos-join | (c) Meredith-type | (d/e) snark-completion | sum-check |",
    "|---:|---:|---:|---:|---:|---:|:---:|",
  ]
  for order_string in sorted(report["orders"], key=lambda item: int(item)):
    row = report["orders"][order_string]
    order = int(order_string)
    snark_count = row["d_snark"] if order % 2 else row["e_snark"]
    lines.append(
      "| "
      f"{order} | {row['survivor_count']} | {row['a_vertex_blowup']} | "
      f"{row['b_hajos']} | {row['c_meredith']} | {snark_count} | "
      f"{'PASS' if row['sum_check'] else 'FAIL'} |"
    )
  lines.append("")
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text("\n".join(lines), encoding="utf-8")


def write_json(report: dict[str, Any], path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--orders", type=int, nargs="+", default=DEFAULT_ORDERS)
  parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
  parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD_OUTPUT)
  parser.add_argument("--sample-limit", type=int, default=3)
  return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
  args = parse_args(sys.argv[1:] if argv is None else argv)
  report: dict[str, Any] = {
    "orders": {},
    "categories": CATEGORIES,
  }
  for order in sorted(args.orders):
    row = classify_order(order, sample_limit=args.sample_limit)
    report["orders"][str(order)] = row
    status = "PASS" if row["sum_check"] else "FAIL"
    print(
      f"order {order}: {status} "
      f"classified={row['total_classified']} survivors={row['survivor_count']} "
      f"a={row['a_vertex_blowup']} b={row['b_hajos']} c={row['c_meredith']} "
      f"d={row['d_snark']} e={row['e_snark']}"
    )
  write_json(report, args.json_output)
  write_markdown(report, args.markdown_output)
  print(f"wrote JSON: {args.json_output}")
  print(f"wrote Markdown: {args.markdown_output}")


if __name__ == "__main__":
  main()
