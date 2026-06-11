from __future__ import annotations

import networkx as nx


def is_bipartite(G: nx.Graph) -> bool:
  return nx.is_bipartite(G)


def is_regular(G: nx.Graph) -> bool:
  degrees = set(d for _, d in G.degree())
  return len(degrees) == 1


def has_cutvertex(G: nx.Graph) -> bool:
  return len(list(nx.articulation_points(G))) > 0


def exceeds_chetwynd_hilton(G: nx.Graph) -> bool:
  n = G.number_of_nodes()
  delta = max(d for _, d in G.degree())
  return delta >= n - 3


def exceeds_arxiv_threshold(G: nx.Graph) -> bool:
  """Exclude if Delta >= (2n + 5*delta_min - 12)/3. From arXiv:2512.07252."""
  n = G.number_of_nodes()
  delta_max = max(d for _, d in G.degree())
  delta_min = min(d for _, d in G.degree())
  threshold = (2 * n + 5 * delta_min - 12) / 3
  return delta_max >= threshold


def passes_all_filters(G: nx.Graph) -> bool:
  if is_bipartite(G):
    return False
  if is_regular(G):
    return False
  if has_cutvertex(G):
    return False
  if exceeds_chetwynd_hilton(G):
    return False
  if exceeds_arxiv_threshold(G):
    return False
  return True
