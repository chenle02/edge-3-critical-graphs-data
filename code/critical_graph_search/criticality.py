from __future__ import annotations

import networkx as nx

from .edge_coloring import (
  _is_k_edge_colorable_from_endpoints,
  _prepare_endpoints,
  is_class2,
  is_k_edge_colorable,
)


def is_delta_critical(G: nx.Graph) -> bool:
  if not nx.is_connected(G):
    return False
  if any(d < 2 for _, d in G.degree()):
    return False
  if any(nx.bridges(G)):
    return False

  delta = max(d for _, d in G.degree())
  if delta <= 1:
    return False

  edge_endpoints, n_vertices = _prepare_endpoints(G)

  if _is_k_edge_colorable_from_endpoints(edge_endpoints, n_vertices, delta):
    return False

  for skip_idx in range(len(edge_endpoints)):
    if not _is_k_edge_colorable_from_endpoints(edge_endpoints, n_vertices, delta, skip_idx=skip_idx):
      return False
  return True
