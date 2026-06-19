#!/usr/bin/env python3
"""Render publication-quality images of edge-chromatic 3-critical graphs.

Inputs are the read-only census JSON/JSON.GZ files in shared/data.  Outputs are
PNG figures and an INSTALL_MANIFEST.md under this render directory.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image


DEFAULT_DATA_DIR = Path("/tmp/opencode/e3c/shared/data")
DEFAULT_OUTPUT_DIR = Path("/tmp/opencode/e3c/render/figures")
DEFAULT_MANIFEST = Path("/tmp/opencode/e3c/render/INSTALL_MANIFEST.md")
WITNESS_ORDER_25_GRAPH6 = "X???C@?K@OOae?DOGP@D?QO?C????G??G??A?G?G??A_??P?_?@"

ORANGE = "#f5a623"
EDGE_GRAY = "#777777"
TITLE_COLOR = "#222222"


def load_census(order: int, data_dir: Path) -> dict:
  """Load a census file for one order, accepting JSON or JSON.GZ."""
  json_path = data_dir / f"order_{order}_delta_3.json"
  gz_path = data_dir / f"order_{order}_delta_3.json.gz"
  if json_path.exists():
    with json_path.open("r", encoding="utf-8") as handle:
      return json.load(handle)
  if gz_path.exists():
    with gzip.open(gz_path, "rt", encoding="utf-8") as handle:
      return json.load(handle)
  raise FileNotFoundError(f"No census file for order {order}: {json_path} or {gz_path}")


def graph_from_edges(edges: Iterable[Iterable[int]], n: int) -> nx.Graph:
  graph = nx.Graph()
  graph.add_nodes_from(range(n))
  graph.add_edges_from((int(u), int(v)) for u, v in edges)
  return graph


def realized_degrees(edges: Iterable[Iterable[int]], n: int) -> list[int]:
  degrees = [0] * n
  for u, v in edges:
    degrees[int(u)] += 1
    degrees[int(v)] += 1
  return degrees


def graph_girth(graph: nx.Graph) -> int | None:
  """Return the length of a shortest cycle, or None for forests."""
  cycles = nx.cycle_basis(graph)
  if not cycles:
    return None
  return min(len(cycle) for cycle in cycles)


def stable_layout(graph: nx.Graph) -> dict[int, np.ndarray]:
  """Deterministic layout with a stable circular fallback for tiny edge cases."""
  if graph.number_of_nodes() <= 2 or graph.number_of_edges() == 0:
    return nx.circular_layout(graph)
  try:
    return nx.kamada_kawai_layout(graph, weight=None)
  except Exception:
    return nx.spring_layout(graph, seed=314159, iterations=250)


def draw_graph(ax: plt.Axes, edges: list[list[int]], n: int, title: str) -> None:
  """Draw one graph panel; degree-2 vertices are orange and degree-3 vertices white."""
  graph = graph_from_edges(edges, n)
  degrees = realized_degrees(edges, n)
  pos = stable_layout(graph)
  degree2 = [node for node, degree in enumerate(degrees) if degree == 2]
  other = [node for node in graph.nodes if node not in degree2]

  nx.draw_networkx_edges(graph, pos, ax=ax, edge_color=EDGE_GRAY, width=0.8, alpha=0.88)
  nx.draw_networkx_nodes(
    graph,
    pos,
    nodelist=other,
    ax=ax,
    node_color="white",
    edgecolors="black",
    linewidths=0.7,
    node_size=92,
  )
  nx.draw_networkx_nodes(
    graph,
    pos,
    nodelist=degree2,
    ax=ax,
    node_color=ORANGE,
    edgecolors="black",
    linewidths=0.7,
    node_size=102,
  )
  if n <= 13:
    nx.draw_networkx_labels(graph, pos, ax=ax, font_size=4.7, font_color="#111111")
  ax.set_title(title, fontsize=7.2, color=TITLE_COLOR, pad=2.5, fontweight="semibold")
  ax.set_axis_off()
  ax.set_aspect("equal")


def panel_title(order: int, idx: int, survivor: dict, *, include_girth: bool) -> str:
  title = f"n={order}  #{idx}  α={survivor.get('alpha', '?')}"
  if include_girth:
    graph = graph_from_edges(survivor["edges"], order)
    girth = graph_girth(graph)
    title += f"  g={girth if girth is not None else '∞'}"
  return title


def select_even_sample(items: list[dict], limit: int) -> list[tuple[int, dict]]:
  """Deterministically choose up to limit survivors spread across the census order."""
  if len(items) <= limit:
    return [(idx + 1, item) for idx, item in enumerate(items)]
  positions = np.linspace(0, len(items) - 1, num=limit, dtype=int)
  seen: set[int] = set()
  selected: list[tuple[int, dict]] = []
  for pos in positions:
    if int(pos) in seen:
      continue
    seen.add(int(pos))
    selected.append((int(pos) + 1, items[int(pos)]))
  return selected


def grid_shape(count: int, preferred_cols: int | None = None) -> tuple[int, int]:
  if count <= 0:
    return (0, 0)
  if preferred_cols is not None:
    cols = min(preferred_cols, count)
  else:
    cols = int(math.ceil(math.sqrt(count)))
  rows = int(math.ceil(count / cols))
  return rows, cols


def render_montage(
  panels: list[tuple[list[list[int]], int, str]],
  output_path: Path,
  *,
  suptitle: str | None = None,
  cols: int | None = None,
  dpi: int = 120,
) -> None:
  rows, cols_actual = grid_shape(len(panels), cols)
  panel_w = 1.72 if len(panels) > 24 else 2.05
  panel_h = 1.55 if len(panels) > 24 else 1.85
  fig_w = max(5.0, cols_actual * panel_w)
  fig_h = max(3.0, rows * panel_h + (0.35 if suptitle else 0.0))
  fig, axes = plt.subplots(rows, cols_actual, figsize=(fig_w, fig_h), dpi=dpi)
  axes_array = np.atleast_1d(axes).reshape(rows, cols_actual)
  for ax in axes_array.ravel():
    ax.set_axis_off()
  for ax, (edges, n, title) in zip(axes_array.ravel(), panels):
    draw_graph(ax, edges, n, title)
  if suptitle:
    fig.suptitle(suptitle, fontsize=12, fontweight="bold", y=0.992, color=TITLE_COLOR)
  fig.patch.set_facecolor("white")
  fig.tight_layout(pad=0.55, h_pad=0.85, w_pad=0.55, rect=(0, 0, 1, 0.965 if suptitle else 1))
  output_path.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(output_path, facecolor="white", bbox_inches="tight", pad_inches=0.08)
  plt.close(fig)


def survivor_panels(
  order: int,
  survivors_with_indices: list[tuple[int, dict]],
  *,
  include_girth: bool,
) -> list[tuple[list[list[int]], int, str]]:
  return [
    (survivor["edges"], order, panel_title(order, idx, survivor, include_girth=include_girth))
    for idx, survivor in survivors_with_indices
  ]


def render_hero(data_by_order: dict[int, dict], output_dir: Path) -> Path:
  selected: list[tuple[int, int, dict]] = []
  selected.append((9, 1, data_by_order[9]["survivors"][0]))
  selected.extend((11, idx + 1, survivor) for idx, survivor in enumerate(data_by_order[11]["survivors"][:2]))
  selected.extend((13, idx + 1, survivor) for idx, survivor in enumerate(data_by_order[13]["survivors"][:6]))
  panels = [
    (survivor["edges"], order, panel_title(order, idx, survivor, include_girth=False))
    for order, idx, survivor in selected
  ]
  path = output_dir / "hero.png"
  render_montage(panels, path, suptitle="Nontrivial edge-chromatic 3-critical graphs", cols=3, dpi=125)
  return path


def render_gallery(order: int, data: dict, output_dir: Path, *, limit: int | None = None) -> Path:
  survivors = data["survivors"]
  true_total = int(data.get("survivor_count", len(survivors)))
  if limit is None:
    chosen = [(idx + 1, survivor) for idx, survivor in enumerate(survivors)]
    filename = f"gallery_order_{order:02d}.png"
    suptitle = f"Order {order}: all {true_total} survivors"
  else:
    chosen = select_even_sample(survivors, min(limit, len(survivors)))
    if order in (19, 21):
      filename = f"gallery_order_{order:02d}_sample.png"
    else:
      filename = f"gallery_order_{order:02d}.png"
    suptitle = f"Order {order}: sample of {len(chosen)} of {true_total} survivors"
  panels = survivor_panels(order, chosen, include_girth=True)
  cols = 8 if len(panels) > 24 else (6 if len(panels) > 12 else None)
  path = output_dir / filename
  render_montage(panels, path, suptitle=suptitle, cols=cols, dpi=118 if len(panels) > 24 else 125)
  return path


def render_order_22(data: dict, output_dir: Path) -> Path:
  survivor = data["survivors"][0]
  graph = graph_from_edges(survivor["edges"], 22)
  girth = graph_girth(graph)
  title = f"Order 22 survivor  α={survivor.get('alpha', '?')}  g={girth if girth is not None else '∞'}"
  path = output_dir / "order_22_survivor.png"
  render_montage([(survivor["edges"], 22, title)], path, suptitle=None, cols=1, dpi=130)
  return path


def render_witness(output_dir: Path) -> Path:
  graph = nx.from_graph6_bytes(WITNESS_ORDER_25_GRAPH6.encode("ascii"))
  graph = nx.convert_node_labels_to_integers(graph, ordering="sorted")
  edges = [[int(u), int(v)] for u, v in graph.edges()]
  degrees = dict(graph.degree())
  n = graph.number_of_nodes()
  girth = graph_girth(graph)
  degree2_count = sum(1 for degree in degrees.values() if degree == 2)
  title = f"Order 25 impossibility witness  degree-2={degree2_count}  g={girth if girth is not None else '∞'}"
  path = output_dir / "witness_order_25.png"
  render_montage([(edges, n, title)], path, suptitle=None, cols=1, dpi=130)
  return path


def write_manifest(manifest_path: Path) -> None:
  content = """# Install Manifest

All files are generated by `/tmp/opencode/e3c/render/render_graphs.py` and live under `/tmp/opencode/e3c/render/figures/`.

## Public repository `assets/` for the README hero

- `hero.png` -> `assets/hero.png`
- `witness_order_25.png` -> `assets/witness_order_25.png`

## Public repository `docs/assets/figures/` for the docs gallery

- `gallery_order_09.png` -> `docs/assets/figures/gallery_order_09.png`
- `gallery_order_11.png` -> `docs/assets/figures/gallery_order_11.png`
- `gallery_order_13.png` -> `docs/assets/figures/gallery_order_13.png`
- `gallery_order_15.png` -> `docs/assets/figures/gallery_order_15.png`
- `gallery_order_17.png` -> `docs/assets/figures/gallery_order_17.png`
- `gallery_order_19_sample.png` -> `docs/assets/figures/gallery_order_19_sample.png`
- `gallery_order_21_sample.png` -> `docs/assets/figures/gallery_order_21_sample.png`
- `order_22_survivor.png` -> `docs/assets/figures/order_22_survivor.png`
"""
  manifest_path.parent.mkdir(parents=True, exist_ok=True)
  manifest_path.write_text(content, encoding="utf-8")


def verify_pngs(paths: list[Path]) -> list[tuple[str, tuple[int, int], float]]:
  rows: list[tuple[str, tuple[int, int], float]] = []
  for path in paths:
    with Image.open(path) as image:
      size = image.size
      image.verify()
    kb = path.stat().st_size / 1024.0
    rows.append((path.name, size, kb))
  return rows


def print_size_table(rows: list[tuple[str, tuple[int, int], float]]) -> None:
  print("\nFigure size table")
  print("figure | pixels | KB")
  print("--- | --- | ---")
  for name, (width, height), kb in rows:
    print(f"{name} | {width}x{height} | {kb:.1f}")


def render_all(data_dir: Path, output_dir: Path, manifest_path: Path) -> list[Path]:
  orders_needed = [9, 11, 13, 15, 17, 19, 21, 22]
  data_by_order = {order: load_census(order, data_dir) for order in orders_needed}
  paths: list[Path] = []
  paths.append(render_hero(data_by_order, output_dir))
  for order in (9, 11, 13):
    paths.append(render_gallery(order, data_by_order[order], output_dir, limit=None))
  for order in (15, 17):
    paths.append(render_gallery(order, data_by_order[order], output_dir, limit=48))
  for order in (19, 21):
    paths.append(render_gallery(order, data_by_order[order], output_dir, limit=24))
  paths.append(render_order_22(data_by_order[22], output_dir))
  paths.append(render_witness(output_dir))
  write_manifest(manifest_path)
  return paths


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Render README and docs-gallery PNGs for edge-chromatic 3-critical census graphs."
  )
  parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
  parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
  parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
  parser.add_argument("--no-verify", action="store_true", help="Skip Pillow verify and size table.")
  return parser.parse_args()


def main() -> None:
  args = parse_args()
  paths = render_all(args.data_dir, args.output_dir, args.manifest)
  if not args.no_verify:
    rows = verify_pngs(paths)
    print_size_table(rows)
    too_large = [(name, kb) for name, _, kb in rows if kb > 2500.0]
    if too_large:
      details = ", ".join(f"{name}={kb:.1f}KB" for name, kb in too_large)
      raise RuntimeError(f"PNG size limit exceeded: {details}")
    print("\nAll PNGs verify-load successfully.")
  print(f"\nWrote manifest: {args.manifest}")


if __name__ == "__main__":
  main()
