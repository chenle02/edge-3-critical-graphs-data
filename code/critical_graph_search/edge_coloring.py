from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

import networkx as nx

Edge = Tuple[int, int]


def _norm_edge(u: int, v: int) -> Edge:
  return (u, v) if u < v else (v, u)


def _is_k_edge_colorable_reference(G: nx.Graph, k: int) -> bool:
  """Reference backtracking edge-colorability check for simple graphs."""
  if G.number_of_edges() == 0:
    return True

  edges: List[Edge] = [_norm_edge(int(u), int(v)) for u, v in G.edges()]
  incident: Dict[int, List[Edge]] = defaultdict(list)
  for e in edges:
    u, v = e
    incident[u].append(e)
    incident[v].append(e)

  colors: Dict[Edge, int] = {}

  def available_colors(e: Edge) -> List[int]:
    u, v = e
    used = set()
    for ie in incident[u]:
      if ie in colors:
        used.add(colors[ie])
    for ie in incident[v]:
      if ie in colors:
        used.add(colors[ie])
    return [c for c in range(k) if c not in used]

  def pick_uncolored_edge() -> Edge:
    best = None
    best_domain = None
    for e in edges:
      if e in colors:
        continue
      domain = available_colors(e)
      if best is None or len(domain) < len(best_domain):
        best = e
        best_domain = domain
        if len(best_domain) <= 1:
          break
    return best  # type: ignore[return-value]

  def dfs() -> bool:
    if len(colors) == len(edges):
      return True
    e = pick_uncolored_edge()
    domain = available_colors(e)
    if not domain:
      return False
    for c in domain:
      colors[e] = c
      if dfs():
        return True
      del colors[e]
    return False

  return dfs()


def _prepare_endpoints(G: nx.Graph) -> Tuple[List[Tuple[int, int]], int]:
  edges = [_norm_edge(int(u), int(v)) for u, v in G.edges()]
  vertices = sorted({v for e in edges for v in e})
  vertex_to_idx = {vertex: idx for idx, vertex in enumerate(vertices)}
  edge_endpoints = [(vertex_to_idx[u], vertex_to_idx[v]) for u, v in edges]
  return edge_endpoints, len(vertices)


def _is_k_edge_colorable_from_endpoints(
  edge_endpoints: List[Tuple[int, int]],
  n_vertices: int,
  k: int,
  skip_idx: int = -1,
) -> bool:
  edge_count = len(edge_endpoints)
  if edge_count == 0 or (edge_count == 1 and skip_idx == 0):
    return True
  full_mask = (1 << k) - 1
  edge_colors = [-1] * edge_count
  if skip_idx >= 0:
    edge_colors[skip_idx] = -2

  vertex_masks = [0] * n_vertices
  active_count = edge_count - (1 if skip_idx >= 0 else 0)
  colored_edges = 0

  def iter_colors(mask: int) -> List[int]:
    colors: List[int] = []
    while mask:
      lsb = mask & -mask
      colors.append(lsb.bit_length() - 1)
      mask ^= lsb
    return colors

  def available_mask(edge_idx: int) -> int:
    u_idx, v_idx = edge_endpoints[edge_idx]
    return full_mask & ~(vertex_masks[u_idx] | vertex_masks[v_idx])

  def pick_uncolored_edge() -> int:
    best_idx = -1
    best_domain_size = k + 1
    for idx in range(edge_count):
      if edge_colors[idx] != -1:
        continue
      domain_mask = available_mask(idx)
      domain_size = domain_mask.bit_count()
      if domain_size < best_domain_size:
        best_idx = idx
        best_domain_size = domain_size
        if domain_size <= 1:
          break
    return best_idx

  def dfs() -> bool:
    nonlocal colored_edges
    if colored_edges == active_count:
      return True
    edge_idx = pick_uncolored_edge()
    domain_mask = available_mask(edge_idx)
    if domain_mask == 0:
      return False
    u_idx, v_idx = edge_endpoints[edge_idx]
    for color in iter_colors(domain_mask):
      bit = 1 << color
      edge_colors[edge_idx] = color
      vertex_masks[u_idx] |= bit
      vertex_masks[v_idx] |= bit
      colored_edges += 1
      if dfs():
        return True
      colored_edges -= 1
      vertex_masks[u_idx] ^= bit
      vertex_masks[v_idx] ^= bit
      edge_colors[edge_idx] = -1
    return False

  return dfs()


def _is_k_edge_colorable_fast(G: nx.Graph, k: int) -> bool:
  if G.number_of_edges() == 0:
    return True
  edge_endpoints, n_vertices = _prepare_endpoints(G)
  return _is_k_edge_colorable_from_endpoints(edge_endpoints, n_vertices, k)


def is_k_edge_colorable(G: nx.Graph, k: int, implementation: str = "fast") -> bool:
  if implementation == "reference":
    return _is_k_edge_colorable_reference(G, k)
  if implementation == "fast":
    return _is_k_edge_colorable_fast(G, k)
  raise ValueError(f"Unknown edge-coloring implementation: {implementation}")


def is_class2(G: nx.Graph, implementation: str = "fast") -> bool:
  """Class 2 iff not Δ-edge-colorable where Δ = max degree."""
  delta = max((d for _, d in G.degree()), default=0)
  if delta <= 1:
    return False
  return not is_k_edge_colorable(G, delta, implementation=implementation)
