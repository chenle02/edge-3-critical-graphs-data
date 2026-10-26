#!/usr/bin/env python3
"""Verify that the nontrivial Delta=3 critical survivors contain P* (the
Petersen graph minus a vertex) as a minor.

Because P* has maximum degree 3, a graph contains P* as a minor if and only if
it contains a subdivision of P*.  The search below is a backtracking search for
such a subdivision (branch vertices placed one at a time along a BFS order of
the edges of P*, paths routed through unused vertices).

Which graphs are searched directly:
  * every survivor of order at most 17 (and the order-9 and order-11 graphs);
  * every survivor of orders >= 19 whose exact first-applicable clause is
    (d) or (e) (clauses computed by classify_census_characterization_exact).
Every other survivor falls under clause (a), (b) or (c) and therefore contains
a smaller nontrivial 3-critical graph as a minor (contract the independent
triangle, the part coming from the other Hajos summand, or the inserted graph
of the Meredith-type extension), so by induction on the order it contains P*.

Place this file next to classify_census_characterization_exact.py and run from
the repository root:

    python3 code/scripts/verify_pstar_minor.py --orders 9 11 13 15 17 19 21 22 23 24
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent))
import classify_census_characterization_exact as cce  # noqa: E402

REPORTS = cce.REPORTS
DEFAULT_ORDERS = [9, 11, 13, 15, 17, 19, 21, 22, 23, 24]
DIRECT_ORDERS = {9, 11, 13, 15, 17}


def pstar() -> nx.Graph:
  P = nx.petersen_graph()
  P.remove_node(0)
  return P


class Budget(Exception):
  pass


def contains_subdivision(G: nx.Graph, H: nx.Graph, start_vertex, max_nodes: int):
  """True if a subdivision of H with the first branch vertex at start_vertex is
  found; False if exhaustively excluded; None if the node budget ran out."""
  adj = {v: list(G.neighbors(v)) for v in G.nodes()}
  degG = dict(G.degree())
  degH = dict(H.degree())
  start = max(H.nodes(), key=lambda v: degH[v])
  order: list[tuple[int, int]] = []
  placed = {start}
  queue = [start]
  seen: set[frozenset] = set()
  while queue:
    a = queue.pop(0)
    for b in H.neighbors(a):
      e = frozenset((a, b))
      if e in seen:
        continue
      seen.add(e)
      order.append((a, b))
      if b not in placed:
        placed.add(b)
        queue.append(b)
  img = {start: start_vertex}
  used = {start_vertex}
  budget = [0]

  def paths_from(s, target):
    stack = [(s, [s])]
    while stack:
      v, path = stack.pop()
      for w in adj[v]:
        if w in path:
          continue
        if target is not None:
          if w == target:
            yield path + [w]
            continue
          if w in used:
            continue
          stack.append((w, path + [w]))
        else:
          if w in used:
            continue
          yield path + [w]
          stack.append((w, path + [w]))

  def rec(k: int) -> bool:
    budget[0] += 1
    if budget[0] > max_nodes:
      raise Budget()
    if k == len(order):
      return True
    a, b = order[k]
    s = img[a]
    if b in img:
      for path in paths_from(s, img[b]):
        interior = path[1:-1]
        used.update(interior)
        if rec(k + 1):
          return True
        used.difference_update(interior)
      return False
    for path in paths_from(s, None):
      w = path[-1]
      if degG[w] < degH[b]:
        continue
      interior = path[1:-1]
      img[b] = w
      used.add(w)
      used.update(interior)
      if rec(k + 1):
        return True
      used.difference_update(interior)
      used.discard(w)
      del img[b]
    return False

  try:
    return rec(0)
  except Budget:
    return None


def has_pstar_minor(G: nx.Graph, max_nodes: int = 3_000_000) -> bool | None:
  H = pstar()
  undecided = False
  for v0 in [v for v in G.nodes() if G.degree(v) == 3]:
    r = contains_subdivision(G, H, v0, max_nodes)
    if r:
      return True
    if r is None:
      undecided = True
  return None if undecided else False


def work(args):
  order, g6, direct = args
  G = nx.from_graph6_bytes(g6.encode())
  assert G.number_of_nodes() == order
  if direct:
    clause = None
  else:
    clause = cce.exact_classify(G)
    if clause not in "de":
      return g6, clause, "by induction"
  r = has_pstar_minor(G)
  return g6, clause, {True: "contains P*", False: "NO P* MINOR", None: "undecided"}[r]


def main(argv=None):
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--orders", type=int, nargs="+", default=DEFAULT_ORDERS)
  parser.add_argument("--processes", type=int, default=2)
  parser.add_argument("--json-output", type=Path, default=REPORTS / "pstar_minor_verification.json")
  args = parser.parse_args(sys.argv[1:] if argv is None else argv)
  report = {}
  with Pool(args.processes) as pool:
    for order in sorted(args.orders):
      t0 = time.time()
      g6s = cce.load_graph6_list(order)
      direct = order in DIRECT_ORDERS
      results = pool.map(work, [(order, g, direct) for g in g6s], chunksize=16)
      counts = {}
      bad = []
      for g6, clause, verdict in results:
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict in ("NO P* MINOR", "undecided"):
          bad.append({"graph6": g6, "clause": clause, "verdict": verdict})
      report[str(order)] = {"survivors": len(g6s), "searched_directly": direct or "clauses (d)/(e) only",
                            "verdicts": counts, "problems": bad, "seconds": round(time.time() - t0, 1)}
      print(f"order {order}: {report[str(order)]}", flush=True)
  args.json_output.parent.mkdir(parents=True, exist_ok=True)
  args.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
  print(f"wrote {args.json_output}")


if __name__ == "__main__":
  main()
