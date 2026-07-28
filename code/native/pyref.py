#!/usr/bin/python3
"""Reference survivor filter: reads geng graph6 on stdin, writes survivor graph6.

Uses the exact Python census predicates (pruning + criticality + overfull) so the
native C filter can be checked against it for bit-equality (docs/DECISIONS.md
D-0002, native/validate.sh). This is the ground truth the C filter must match.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import networkx as nx  # noqa: E402

from critical_graph_search.pruning import passes_all_filters  # noqa: E402
from critical_graph_search.criticality import is_delta_critical  # noqa: E402
from critical_graph_search.density_filter import has_overfull_subgraph  # noqa: E402


def main() -> None:
  for line in sys.stdin:
    line = line.strip()
    if not line or line[0] == ">":
      continue
    graph = nx.from_graph6_bytes(line.encode("ascii"))
    if max(d for _, d in graph.degree()) != 3:
      continue
    if not passes_all_filters(graph):
      continue
    if not is_delta_critical(graph):
      continue
    if has_overfull_subgraph(graph, delta=3, stop_on_first=True)[0]:
      continue
    sys.stdout.write(line + "\n")


if __name__ == "__main__":
  main()
