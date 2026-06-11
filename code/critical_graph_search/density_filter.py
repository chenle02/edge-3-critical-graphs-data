from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from typing import List, Tuple

import networkx as nx


def _has_overfull_subgraph_reference(
  G: nx.Graph,
  delta: int,
  stop_on_first: bool = True,
) -> Tuple[bool, List[List[int]]]:
  """Reference implementation using induced-subgraph enumeration."""
  nodes = list(G.nodes())
  n = len(nodes)
  violating: List[List[int]] = []

  for r in range(1, n + 1, 2):
    threshold = delta * (r // 2)
    for comb in combinations(range(n), r):
      subset = [nodes[i] for i in comb]
      m = G.subgraph(subset).number_of_edges()
      if m > threshold:
        violating.append(subset)
        if stop_on_first:
          return True, violating
  return (len(violating) > 0), violating


def _adjacency_masks(G: nx.Graph) -> Tuple[List[int], List[int]]:
  nodes = [int(node) for node in G.nodes()]
  node_to_idx = {node: idx for idx, node in enumerate(nodes)}
  adj = [0] * len(nodes)
  for u, v in G.edges():
    ui = node_to_idx[int(u)]
    vi = node_to_idx[int(v)]
    adj[ui] |= 1 << vi
    adj[vi] |= 1 << ui
  return nodes, adj


@lru_cache(maxsize=None)
def _odd_subset_masks_by_size(n: int) -> Tuple[Tuple[int, ...], ...]:
  grouped: List[Tuple[int, ...]] = [tuple() for _ in range(n + 1)]
  mutable_groups: List[List[int]] = [[] for _ in range(n + 1)]
  for r in range(1, n + 1, 2):
    for comb in combinations(range(n), r):
      mask = 0
      for idx in comb:
        mask |= 1 << idx
      mutable_groups[r].append(mask)
  for r in range(n + 1):
    grouped[r] = tuple(mutable_groups[r])
  return tuple(grouped)


def _edge_count_in_subset(mask: int, adj: List[int]) -> int:
  edges = 0
  remaining = mask
  while remaining:
    lsb = remaining & -remaining
    idx = lsb.bit_length() - 1
    remaining ^= lsb
    edges += (adj[idx] & remaining).bit_count()
  return edges


def _mask_to_subset(mask: int, nodes: List[int]) -> List[int]:
  return [nodes[idx] for idx in range(len(nodes)) if (mask >> idx) & 1]


def _has_overfull_subgraph_fast(
  G: nx.Graph,
  delta: int,
  stop_on_first: bool = True,
) -> Tuple[bool, List[List[int]]]:
  """Bitset implementation specialized for small fixed-order simple graphs."""
  nodes, adj = _adjacency_masks(G)
  n = len(nodes)
  violating: List[List[int]] = []
  subset_groups = _odd_subset_masks_by_size(n)

  for r in range(1, n + 1, 2):
    threshold = delta * (r // 2)
    for mask in subset_groups[r]:
      if _edge_count_in_subset(mask, adj) > threshold:
        subset = _mask_to_subset(mask, nodes)
        violating.append(subset)
        if stop_on_first:
          return True, violating
  return (len(violating) > 0), violating


def has_overfull_subgraph(
  G: nx.Graph,
  delta: int,
  stop_on_first: bool = True,
  implementation: str = "fast",
) -> Tuple[bool, List[List[int]]]:
  """Check odd-cardinality induced subgraphs for overfull inequality."""
  if implementation == "reference":
    return _has_overfull_subgraph_reference(G, delta=delta, stop_on_first=stop_on_first)
  if implementation == "fast":
    return _has_overfull_subgraph_fast(G, delta=delta, stop_on_first=stop_on_first)
  raise ValueError(f"Unknown density-filter implementation: {implementation}")
