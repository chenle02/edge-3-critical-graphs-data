#!/usr/bin/env python3
"""Exact first-applicable classification of the nontrivial Delta=3 critical
survivors by the clauses of the characterization theorem, following the
procedure described in the paper's appendix:

1. an independent triangle gives clause (a);
2. otherwise any triangle or any cyclic 2-edge-cut gives clause (b);
3. otherwise a cyclic 3-edge-cut one of whose two shores (EITHER shore)
   contains no vertex of degree 2 gives clause (c);
4. the remaining records receive clause (d) for odd order and clause (e)
   for even order.

This differs from classify_census_characterization.py only in rule 3, which
there inspects only subset-minimal *smaller* shores and therefore lists some
clause-(c) graphs under (d)/(e).  Here every cyclic 3-edge-cut and both of its
shores are examined, so the labels are an exact partition by the first
applicable theorem clause.

For every survivor the script also records the number t of degree-2 vertices,
and for every (d)/(e) survivor it verifies that the snark completion of the
paper's Lemma 3.1 exists: for odd order, a new vertex joined to three degree-2
vertices plus a pairing of the remaining ones; for even order, a pairing of all
degree-2 vertices.  A snark here means a cubic, triangle-free, cyclically
4-edge-connected graph of class 2.

Place this file next to classify_census_characterization.py and run from the
repository root, e.g.

    python3 code/scripts/classify_census_characterization_exact.py --orders 13 15 17 19 21 22 23 24
"""

from __future__ import annotations

import argparse
import gc
import gzip
import itertools
import json
import re
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
from typing import Any

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify_census_characterization as ccc  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
RESULTS = REPO_ROOT / "results"
REPORTS = REPO_ROOT / "reports"

DEFAULT_ORDERS = [13, 15, 17, 19, 21, 22, 23]
DEFAULT_JSON_OUTPUT = REPORTS / "census_characterization_classification_exact.json"
DEFAULT_MD_OUTPUT = REPORTS / "census_characterization_classification_exact.md"


# ---------------------------------------------------------------- classify

def exact_classify(graph: nx.Graph) -> str:
  order = graph.number_of_nodes()
  triangles = ccc.all_triangles(graph)
  if ccc.independent_triangles(graph, triangles):
    return "a"
  if triangles:
    return "b"
  edges, adjacency = ccc.edge_data(graph)
  if ccc.has_cyclic_2_edge_cut(order, edges, adjacency):
    return "b"
  degrees = dict(graph.degree())
  for cut in itertools.combinations(range(len(edges)), 3):
    components = ccc.cyclic_cut_components(order, edges, adjacency, cut)
    if components is None:
      continue
    first, second = components
    if all(degrees[v] == 3 for v in first) or all(degrees[v] == 3 for v in second):
      return "c"
  return "d" if order % 2 else "e"


# ------------------------------------------------------------- snark check

def three_edge_colorable(graph: nx.Graph) -> bool:
  start = next(iter(graph.nodes()))
  order_: list[tuple[int, int]] = []
  seen: set[tuple[int, int]] = set()
  for u, v in nx.edge_bfs(graph, source=start):
    e = (u, v) if u < v else (v, u)
    if e not in seen:
      seen.add(e)
      order_.append(e)
  assert len(order_) == graph.number_of_edges()
  used = {v: set() for v in graph.nodes()}

  def rec(i: int) -> bool:
    if i == len(order_):
      return True
    u, v = order_[i]
    for c in (0, 1, 2):
      if c not in used[u] and c not in used[v]:
        used[u].add(c)
        used[v].add(c)
        if rec(i + 1):
          return True
        used[u].discard(c)
        used[v].discard(c)
    return False

  return rec(0)


def cyclically_k_edge_connected(graph: nx.Graph, k: int) -> bool:
  n = graph.number_of_nodes()
  edges, adjacency = ccc.edge_data(graph)
  for size in range(0, k):
    for cut in itertools.combinations(range(len(edges)), size):
      comps = ccc.component_data(n, adjacency, cut, stop_after_three=False)
      if sum(1 for verts, ne in comps if ne >= len(verts)) > 1:
        return False
  return True


def is_snark(graph: nx.Graph) -> bool:
  if any(d != 3 for _, d in graph.degree()):
    return False
  if ccc.all_triangles(graph):
    return False
  if not cyclically_k_edge_connected(graph, 4):
    return False
  return not three_edge_colorable(graph)


def pairings(items: list[int]):
  if not items:
    yield []
    return
  a = items[0]
  for i in range(1, len(items)):
    rest = items[1:i] + items[i + 1:]
    for p in pairings(rest):
      yield [(a, items[i])] + p


def completion_is_snark(graph: nx.Graph) -> bool:
  n = graph.number_of_nodes()
  deg2 = [v for v, d in graph.degree() if d == 2]
  if n % 2:
    for triple in itertools.combinations(deg2, 3):
      rest = [v for v in deg2 if v not in triple]
      for p in pairings(rest):
        h = graph.copy()
        h.add_edges_from((n, z) for z in triple)
        h.add_edges_from(p)
        if is_snark(h):
          return True
    return False
  for p in pairings(deg2):
    h = graph.copy()
    h.add_edges_from(p)
    if is_snark(h):
      return True
  return False


# ------------------------------------------------------------------ driver

def load_graph6_list(order: int) -> list[str]:
  path = ccc.result_path_for_order(order)
  text = gzip.open(path, "rt", encoding="utf-8").read() if path.suffix == ".gz" else path.read_text(encoding="utf-8")
  graph6 = re.findall(r'"graph6": "([^"]+)"', text)
  m = re.search(r'"survivor_count": (\d+)', text)
  del text
  gc.collect()
  if m is None or len(graph6) != int(m.group(1)):
    raise AssertionError(f"{path}: found {len(graph6)} graph6 strings, survivor_count {m and m.group(1)}")
  return graph6


def work(args: tuple[int, list[str]]) -> tuple[Counter, dict]:
  order, g6list = args
  counts: Counter = Counter()
  examples: dict = {}
  for g6 in g6list:
    graph = nx.from_graph6_bytes(g6.encode())
    assert graph.number_of_nodes() == order
    clause = exact_classify(graph)
    t = sum(1 for _, d in graph.degree() if d == 2)
    key = (clause, t, completion_is_snark(graph) if clause in "de" else None)
    counts[key] += 1
    examples.setdefault(key, g6)
  return counts, examples


def classify_order(order: int, nproc: int, chunk: int) -> dict[str, Any]:
  graph6 = load_graph6_list(order)
  chunks = [(order, graph6[i:i + chunk]) for i in range(0, len(graph6), chunk)]
  total: Counter = Counter()
  examples: dict = {}
  t0 = time.time()
  with Pool(nproc) as pool:
    for counts, ex in pool.imap_unordered(work, chunks):
      total.update(counts)
      for k, v in ex.items():
        examples.setdefault(k, v)
  by_clause = Counter()
  by_clause_t = Counter()
  snark_ok = Counter()
  for (clause, t, ok), n in total.items():
    by_clause[clause] += n
    by_clause_t[f"({clause}) t={t}"] += n
    if clause in "de":
      snark_ok["completion is a snark" if ok else "NO snark completion"] += n
  row = {
    "survivor_count": len(graph6),
    **{f"clause_{c}": int(by_clause[c]) for c in "abcde"},
    "sum_check": sum(by_clause.values()) == len(graph6),
    "degree2_counts_by_clause": dict(sorted(by_clause_t.items())),
    "snark_completion_check": dict(snark_ok),
    "examples": {f"({c}) t={t}": g for (c, t, _), g in sorted(examples.items())},
    "seconds": round(time.time() - t0, 1),
  }
  if not row["sum_check"]:
    raise AssertionError(f"order {order}: clause counts do not sum to survivor count")
  return row


def write_markdown(report: dict[str, Any], path: Path) -> None:
  lines = [
    "# Exact census characterization classification",
    "",
    "First-applicable theorem clause, with clause (c) tested over every cyclic",
    "3-edge-cut and either shore.  t = number of degree-2 vertices.",
    "",
    "| Order n | survivors | (a) | (b) | (c) | (d) | (e) | t by clause | snark completion of (d)/(e) |",
    "|---:|---:|---:|---:|---:|---:|---:|:---|:---|",
  ]
  for order_string in sorted(report["orders"], key=int):
    row = report["orders"][order_string]
    lines.append(
      f"| {order_string} | {row['survivor_count']} | {row['clause_a']} | {row['clause_b']} | "
      f"{row['clause_c']} | {row['clause_d']} | {row['clause_e']} | "
      f"{', '.join(f'{k}:{v}' for k, v in row['degree2_counts_by_clause'].items())} | "
      f"{', '.join(f'{k}:{v}' for k, v in row['snark_completion_check'].items()) or '-'} |"
    )
  lines.append("")
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--orders", type=int, nargs="+", default=DEFAULT_ORDERS)
  parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
  parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD_OUTPUT)
  parser.add_argument("--processes", type=int, default=2)
  parser.add_argument("--chunk", type=int, default=2000)
  args = parser.parse_args(sys.argv[1:] if argv is None else argv)
  report: dict[str, Any] = {"orders": {}}
  for order in sorted(args.orders):
    row = classify_order(order, args.processes, args.chunk)
    report["orders"][str(order)] = row
    print(
      f"order {order}: a={row['clause_a']} b={row['clause_b']} c={row['clause_c']} "
      f"d={row['clause_d']} e={row['clause_e']} | {row['degree2_counts_by_clause']} | "
      f"{row['snark_completion_check']} ({row['seconds']}s)",
      flush=True,
    )
  args.json_output.parent.mkdir(parents=True, exist_ok=True)
  args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  write_markdown(report, args.markdown_output)
  print(f"wrote JSON: {args.json_output}")
  print(f"wrote Markdown: {args.markdown_output}")


if __name__ == "__main__":
  main()
