#!/usr/bin/python3
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
RESULTS_DIR = ROOT / "results"
REPORTS_DIR = REPO_ROOT / ".hermes" / "reports"
ASSETS_DIR = REPO_ROOT / "notes" / "assets"
COLORS = (1, 2, 3)
Edge = tuple[int, int]


def norm_edge(u: int, v: int) -> Edge:
  u = int(u)
  v = int(v)
  return (u, v) if u < v else (v, u)


def graph6_string(graph: nx.Graph) -> str:
  normalized = nx.convert_node_labels_to_integers(graph, ordering="sorted")
  return nx.to_graph6_bytes(normalized, header=False).decode("ascii").strip()


def graph_from_survivor(survivor: dict[str, Any]) -> nx.Graph:
  graph = nx.Graph()
  graph.add_edges_from(norm_edge(u, v) for u, v in survivor["edges"])
  return nx.convert_node_labels_to_integers(graph, ordering="sorted")


def cycle_rank(graph: nx.Graph) -> int:
  return graph.number_of_edges() - graph.number_of_nodes() + nx.number_connected_components(graph)


def has_cycle(graph: nx.Graph) -> bool:
  return cycle_rank(graph) > 0


def components_after_removing_edges(graph: nx.Graph, cut_edges: tuple[Edge, ...]) -> list[set[int]]:
  reduced = graph.copy()
  reduced.remove_edges_from(cut_edges)
  return [set(map(int, component)) for component in nx.connected_components(reduced)]


def is_cyclic_edge_cut(graph: nx.Graph, cut_edges: tuple[Edge, ...]) -> bool:
  components = components_after_removing_edges(graph, cut_edges)
  if len(components) < 2:
    return False
  return sum(has_cycle(graph.subgraph(component).copy()) for component in components) >= 2


def has_cyclic_edge_cut_smaller_than_3(graph: nx.Graph) -> bool:
  edges = sorted(norm_edge(u, v) for u, v in graph.edges())
  for size in (1, 2):
    for cut_edges in itertools.combinations(edges, size):
      if is_cyclic_edge_cut(graph, cut_edges):
        return True
  return False


def iter_qualifying_h_components(graph: nx.Graph, *, min_h_order: int = 1) -> list[dict[str, Any]]:
  """Return all H components in Songling's request for one graph G.

  H is a component of G-F for a cyclic 3-edge cut F, H contains no original
  degree-2 vertex of G, and H consequently has three degree-2 boundary vertices.
  """
  original_degree2 = {int(v) for v, degree in graph.degree() if degree == 2}
  edges = sorted(norm_edge(u, v) for u, v in graph.edges())
  records: list[dict[str, Any]] = []
  seen: set[tuple[tuple[int, ...], tuple[Edge, ...]]] = set()

  for cut_edges in itertools.combinations(edges, 3):
    components = components_after_removing_edges(graph, cut_edges)
    if len(components) < 2:
      continue
    if sum(has_cycle(graph.subgraph(component).copy()) for component in components) < 2:
      continue
    for component in components:
      if not component.isdisjoint(original_degree2):
        continue
      h = graph.subgraph(component).copy()
      if h.number_of_nodes() < min_h_order:
        continue
      boundary = sorted(int(v) for v, degree in h.degree() if degree == 2)
      if len(boundary) != 3:
        continue
      key = (tuple(sorted(component)), tuple(sorted(cut_edges)))
      if key in seen:
        continue
      seen.add(key)
      records.append(
        {
          "cut_edges": [list(edge) for edge in sorted(cut_edges)],
          "component_vertices_in_G": sorted(component),
          "boundary_vertices_in_G": boundary,
          "h": h,
        }
      )
  return records


def relabel_h_boundary_first(h: nx.Graph, boundary: list[int]) -> tuple[nx.Graph, list[int], dict[int, int]]:
  boundary_sorted = sorted(boundary)
  internal = sorted(v for v in h.nodes() if int(v) not in set(boundary_sorted))
  mapping = {old: new for new, old in enumerate(boundary_sorted + internal)}
  relabeled = nx.relabel_nodes(h, mapping, copy=True)
  return relabeled, [0, 1, 2], mapping


def boundary_cache_key(h: nx.Graph, boundary: list[int]) -> str:
  boundary_sorted = sorted(boundary)
  internal = sorted(v for v in h.nodes() if int(v) not in set(boundary_sorted))
  keys: list[str] = []
  for perm in itertools.permutations(boundary_sorted):
    ordered = list(perm) + internal
    mapping = {old: new for new, old in enumerate(ordered)}
    relabeled = nx.relabel_nodes(h, mapping, copy=True)
    keys.append(graph6_string(relabeled))
  return min(keys)


def condition_key(u: int, v: int, color_pair: tuple[int, int], edge: Edge) -> tuple[int, int, int, int, Edge]:
  a, b = sorted((int(u), int(v)))
  i, j = sorted(color_pair)
  return (a, b, i, j, norm_edge(*edge))


def initial_conditions(boundary: list[int], edges: list[Edge]) -> set[tuple[int, int, int, int, Edge]]:
  conditions: set[tuple[int, int, int, int, Edge]] = set()
  for u, v in itertools.combinations(sorted(boundary), 2):
    for i, j in itertools.combinations(COLORS, 2):
      for edge in edges:
        conditions.add(condition_key(u, v, (i, j), edge))
  return conditions


def mark_covered_by_coloring(
  graph: nx.Graph,
  boundary: list[int],
  edges: list[Edge],
  coloring: dict[Edge, int],
  covered: set[tuple[int, int, int, int, Edge]],
  witnesses: dict[str, dict[str, Any]],
  keep_witnesses: bool,
) -> None:
  boundary_set = set(boundary)
  for i, j in itertools.combinations(COLORS, 2):
    pair = (i, j)
    kempe = nx.Graph()
    kempe.add_nodes_from(graph.nodes())
    for edge in edges:
      if coloring[edge] in pair:
        kempe.add_edge(*edge)
    for component in nx.connected_components(kempe):
      component_set = set(component)
      component_graph = kempe.subgraph(component_set)
      endpoints = sorted(int(v) for v, degree in component_graph.degree() if degree == 1)
      if len(endpoints) != 2:
        continue
      if not set(endpoints).issubset(boundary_set):
        continue
      for edge in component_graph.edges():
        key = condition_key(endpoints[0], endpoints[1], pair, norm_edge(*edge))
        if key in covered:
          continue
        covered.add(key)
        if keep_witnesses:
          witnesses[str(key)] = {
            "boundary_pair": endpoints,
            "color_pair": list(pair),
            "edge": list(norm_edge(*edge)),
            "coloring": {f"{u}-{v}": color for (u, v), color in sorted(coloring.items())},
          }


def test_h_component(h: nx.Graph, boundary: list[int], *, keep_witnesses: bool = False) -> dict[str, Any]:
  h, boundary, _mapping = relabel_h_boundary_first(h, boundary)
  edges = sorted(norm_edge(u, v) for u, v in h.edges())
  target = initial_conditions(boundary, edges)
  covered: set[tuple[int, int, int, int, Edge]] = set()
  witnesses: dict[str, dict[str, Any]] = {}

  incident: dict[int, list[int]] = {int(v): [] for v in h.nodes()}
  for idx, (u, v) in enumerate(edges):
    incident[u].append(idx)
    incident[v].append(idx)

  edge_colors = [-1] * len(edges)
  vertex_used: dict[int, set[int]] = {int(v): set() for v in h.nodes()}
  coloring_count = 0

  def available(edge_idx: int) -> list[int]:
    u, v = edges[edge_idx]
    blocked = vertex_used[u] | vertex_used[v]
    return [color for color in COLORS if color not in blocked]

  def pick_edge() -> int | None:
    best_idx: int | None = None
    best_domain: list[int] | None = None
    for idx in range(len(edges)):
      if edge_colors[idx] != -1:
        continue
      domain = available(idx)
      if best_idx is None or len(domain) < len(best_domain or []):
        best_idx = idx
        best_domain = domain
        if len(domain) <= 1:
          break
    return best_idx

  def dfs(colored_count: int) -> bool:
    nonlocal coloring_count
    if len(covered) == len(target):
      return True
    if colored_count == len(edges):
      coloring_count += 1
      coloring = {edge: edge_colors[idx] for idx, edge in enumerate(edges)}
      mark_covered_by_coloring(h, boundary, edges, coloring, covered, witnesses, keep_witnesses)
      return len(covered) == len(target)
    idx = pick_edge()
    if idx is None:
      return False
    domain = available(idx)
    if not domain:
      return False
    u, v = edges[idx]
    for color in domain:
      edge_colors[idx] = color
      vertex_used[u].add(color)
      vertex_used[v].add(color)
      if dfs(colored_count + 1):
        return True
      vertex_used[v].remove(color)
      vertex_used[u].remove(color)
      edge_colors[idx] = -1
    return False

  passed = dfs(0)
  failed = sorted(target - covered, key=str)
  return {
    "status": "pass" if passed else "fail",
    "h_graph6_boundary_first": graph6_string(h),
    "h_order": h.number_of_nodes(),
    "h_edge_count": h.number_of_edges(),
    "boundary_vertices_boundary_first": boundary,
    "target_condition_count_unordered_colors": len(target),
    "covered_condition_count_unordered_colors": len(covered),
    "proper_3_edge_colorings_examined_until_stop": coloring_count,
    "failed_conditions": [
      {
        "boundary_pair": [item[0], item[1]],
        "color_pair": [item[2], item[3]],
        "edge": list(item[4]),
      }
      for item in failed[:200]
    ],
    "failed_condition_count": len(failed),
    "witnesses": witnesses if keep_witnesses else {},
  }


def load_order(order: int) -> dict[str, Any]:
  path = RESULTS_DIR / f"order_{order}_delta_3.json"
  data = json.loads(path.read_text(encoding="utf-8"))
  survivors = data.get("survivors", [])
  if data.get("survivor_count") != len(survivors):
    raise ValueError(f"order {order} survivor_count mismatch")
  if data.get("processed_graphs") is not None and data.get("generated_biconnected") is not None:
    if data["processed_graphs"] != data["generated_biconnected"]:
      raise ValueError(f"order {order} is not final: processed != generated")
  if data.get("interrupted") is True:
    raise ValueError(f"order {order} result is interrupted")
  return data


def audit_orders(
  orders: list[int],
  *,
  min_h_order: int = 1,
  stop_on_first_fail: bool = False,
  keep_witnesses: bool = False,
) -> dict[str, Any]:
  cache: dict[str, dict[str, Any]] = {}
  order_reports: dict[str, Any] = {}
  first_counterexample: dict[str, Any] | None = None
  total_h = 0
  total_failed_h = 0
  total_graphs_examined = 0

  for order in orders:
    data = load_order(order)
    graph_records: list[dict[str, Any]] = []
    source_summary = {
      "survivor_count": data.get("survivor_count"),
      "generated_biconnected": data.get("generated_biconnected"),
      "processed_graphs": data.get("processed_graphs"),
      "interrupted": data.get("interrupted"),
    }
    skipped_not_cyclically3 = 0
    graphs_with_qualifying_h = 0
    h_count = 0
    failed_h_count = 0

    for index, survivor in enumerate(data["survivors"], start=1):
      graph = graph_from_survivor(survivor)
      total_graphs_examined += 1
      if has_cyclic_edge_cut_smaller_than_3(graph):
        skipped_not_cyclically3 += 1
        continue
      h_records = iter_qualifying_h_components(graph, min_h_order=min_h_order)
      if h_records:
        graphs_with_qualifying_h += 1
      per_graph_h: list[dict[str, Any]] = []
      for h_index, h_record in enumerate(h_records, start=1):
        h_count += 1
        total_h += 1
        cache_key = boundary_cache_key(h_record["h"], h_record["boundary_vertices_in_G"])
        if cache_key not in cache:
          cache[cache_key] = test_h_component(h_record["h"], h_record["boundary_vertices_in_G"], keep_witnesses=keep_witnesses)
        result = cache[cache_key]
        item = {
          "h_index_for_graph": h_index,
          "cut_edges": h_record["cut_edges"],
          "component_vertices_in_G": h_record["component_vertices_in_G"],
          "boundary_vertices_in_G": h_record["boundary_vertices_in_G"],
          "cache_key": cache_key,
          "result": {k: v for k, v in result.items() if k != "witnesses"},
        }
        if result["status"] != "pass":
          failed_h_count += 1
          total_failed_h += 1
          if first_counterexample is None:
            first_counterexample = {
              "order": order,
              "survivor_index": index,
              "survivor_graph6": survivor["graph6"],
              "survivor_edges": survivor["edges"],
              **item,
            }
          if stop_on_first_fail:
            per_graph_h.append(item)
            graph_records.append({"index": index, "graph6": survivor["graph6"], "h_components": per_graph_h})
            order_reports[str(order)] = {
              "source_summary": source_summary,
              "skipped_not_cyclically_3_edge_connected": skipped_not_cyclically3,
              "graphs_with_qualifying_h": graphs_with_qualifying_h,
              "qualifying_h_component_count": h_count,
              "failed_h_component_count": failed_h_count,
              "graphs": graph_records,
            }
            return build_report(orders, order_reports, cache, total_graphs_examined, total_h, total_failed_h, first_counterexample, early_stop=True, min_h_order=min_h_order)
        per_graph_h.append(item)
      if per_graph_h:
        graph_records.append({"index": index, "graph6": survivor["graph6"], "h_components": per_graph_h})

    order_reports[str(order)] = {
      "source_summary": source_summary,
      "skipped_not_cyclically_3_edge_connected": skipped_not_cyclically3,
      "graphs_with_qualifying_h": graphs_with_qualifying_h,
      "qualifying_h_component_count": h_count,
      "failed_h_component_count": failed_h_count,
      "graphs": graph_records,
    }

  return build_report(orders, order_reports, cache, total_graphs_examined, total_h, total_failed_h, first_counterexample, early_stop=False, min_h_order=min_h_order)


def build_report(
  orders: list[int],
  order_reports: dict[str, Any],
  cache: dict[str, dict[str, Any]],
  total_graphs_examined: int,
  total_h: int,
  total_failed_h: int,
  first_counterexample: dict[str, Any] | None,
  *,
  early_stop: bool,
  min_h_order: int,
) -> dict[str, Any]:
  return {
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "scope": {
      "orders": orders,
      "minimum_h_order": min_h_order,
      "source_files": [str(RESULTS_DIR / f"order_{order}_delta_3.json") for order in orders],
      "candidate_filter": f"G is a survivor in order_n_delta_3.json, has no cyclic edge-cut of size 1 or 2, and H is a component of a cyclic 3-edge cut containing no original degree-2 vertex of G, with |V(H)| >= {min_h_order}",
      "kempe_condition": "For each such H, for each pair of its three boundary degree-2 vertices, each unordered color pair {i,j} subset {1,2,3}, and each edge e of H, some proper 3-edge-coloring of H has an (i,j)-Kempe chain with those boundary endpoints containing e. Ordered (i,j) gives the same chain and is therefore covered by the unordered color-pair check.",
    },
    "summary": {
      "total_graphs_examined": total_graphs_examined,
      "total_qualifying_h_components_tested": total_h,
      "unique_boundary_labeled_h_cache_entries": len(cache),
      "failed_h_component_count": total_failed_h,
      "all_tested_h_passed": total_failed_h == 0,
      "early_stop": early_stop,
    },
    "orders": order_reports,
    "cache_summary": {
      "status_counts": dict(Counter(item["status"] for item in cache.values())),
      "h_order_counts": dict(sorted(Counter(item["h_order"] for item in cache.values()).items())),
    },
    "first_counterexample": first_counterexample,
  }


def write_markdown(report: dict[str, Any], path: Path) -> None:
  lines = [
    "# Songling cyclic 3-edge-cut Kempe-chain audit",
    "",
    f"Generated: {report['generated_at']}",
    "",
    "## Scope",
    f"- Orders tested: {report['scope']['orders']}",
    f"- Minimum H order: {report['scope']['minimum_h_order']}",
    f"- Candidate filter: {report['scope']['candidate_filter']}",
    f"- Kempe condition: {report['scope']['kempe_condition']}",
    "",
    "## Summary",
    f"- Total survivor graphs examined: {report['summary']['total_graphs_examined']}",
    f"- Qualifying H components tested: {report['summary']['total_qualifying_h_components_tested']}",
    f"- Unique boundary-labeled H cache entries: {report['summary']['unique_boundary_labeled_h_cache_entries']}",
    f"- Failed H components: {report['summary']['failed_h_component_count']}",
    f"- All tested H passed: {report['summary']['all_tested_h_passed']}",
    f"- Early stop: {report['summary']['early_stop']}",
    "",
    "## By order",
  ]
  for order in report["scope"]["orders"]:
    payload = report["orders"].get(str(order), {})
    if not payload:
      continue
    source = payload["source_summary"]
    lines.extend(
      [
        "",
        f"### Order {order}",
        f"- Source survivor count: {source.get('survivor_count')}",
        f"- Skipped because not cyclically 3-edge connected: {payload['skipped_not_cyclically_3_edge_connected']}",
        f"- Graphs with qualifying H: {payload['graphs_with_qualifying_h']}",
        f"- Qualifying H components: {payload['qualifying_h_component_count']}",
        f"- Failed H components: {payload['failed_h_component_count']}",
      ]
    )
  if report.get("first_counterexample"):
    ce = report["first_counterexample"]
    result = ce["result"]
    lines.extend(
      [
        "",
        "## First counterexample",
        f"- Order: {ce['order']}",
        f"- Survivor index: {ce['survivor_index']}",
        "- Survivor graph6:",
        "  ```",
        f"  {ce['survivor_graph6']}",
        "  ```",
        f"- Cut edges: {ce['cut_edges']}",
        f"- H vertices in G: {ce['component_vertices_in_G']}",
        f"- Boundary vertices in G: {ce['boundary_vertices_in_G']}",
        f"- H graph6 after boundary-first relabeling: `{result['h_graph6_boundary_first']}`",
        f"- Covered/target conditions: {result['covered_condition_count_unordered_colors']}/{result['target_condition_count_unordered_colors']}",
        f"- Failed condition count: {result['failed_condition_count']}",
        "",
        "First failed conditions (boundary-first labels):",
      ]
    )
    for failure in result["failed_conditions"][:20]:
      lines.append(f"- boundary pair {failure['boundary_pair']}, colors {failure['color_pair']}, edge {failure['edge']}")
  else:
    lines.extend(["", "## Counterexamples", "None found in the tested scope."])
  path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_counterexample(report: dict[str, Any], png_path: Path, pdf_path: Path) -> bool:
  ce = report.get("first_counterexample")
  if not ce:
    return False
  import matplotlib.pyplot as plt

  graph = nx.Graph()
  graph.add_edges_from(norm_edge(u, v) for u, v in ce["survivor_edges"])
  h_vertices = set(ce["component_vertices_in_G"])
  boundary = set(ce["boundary_vertices_in_G"])
  cut_edges = {tuple(edge) for edge in ce["cut_edges"]}
  pos = nx.spring_layout(graph, seed=ce["order"] * 1000 + ce["survivor_index"])

  fig, axes = plt.subplots(1, 2, figsize=(13, 6))
  ax = axes[0]
  ax.set_title(f"G order {ce['order']} survivor #{ce['survivor_index']}; cut highlighted")
  node_colors = []
  for node in graph.nodes():
    if node in boundary:
      node_colors.append("#ffcc33")
    elif node in h_vertices:
      node_colors.append("#9ecae1")
    else:
      node_colors.append("#d9d9d9")
  normal_edges = [edge for edge in map(lambda e: norm_edge(*e), graph.edges()) if edge not in cut_edges]
  nx.draw_networkx_nodes(graph, pos, node_color=node_colors, edgecolors="black", ax=ax)
  nx.draw_networkx_edges(graph, pos, edgelist=normal_edges, edge_color="#555555", ax=ax)
  nx.draw_networkx_edges(graph, pos, edgelist=list(cut_edges), edge_color="red", width=3.0, style="dashed", ax=ax)
  nx.draw_networkx_labels(graph, pos, ax=ax, font_size=8)
  ax.axis("off")

  h = graph.subgraph(h_vertices).copy()
  h_pos = {node: pos[node] for node in h.nodes()}
  ax = axes[1]
  ax.set_title("H component; boundary vertices highlighted")
  h_node_colors = ["#ffcc33" if node in boundary else "#9ecae1" for node in h.nodes()]
  nx.draw_networkx_nodes(h, h_pos, node_color=h_node_colors, edgecolors="black", ax=ax)
  nx.draw_networkx_edges(h, h_pos, edge_color="#555555", ax=ax)
  nx.draw_networkx_labels(h, h_pos, ax=ax, font_size=8)
  ax.axis("off")

  fig.suptitle("Counterexample to requested Kempe-chain coverage condition", fontsize=13)
  fig.tight_layout()
  png_path.parent.mkdir(parents=True, exist_ok=True)
  pdf_path.parent.mkdir(parents=True, exist_ok=True)
  fig.savefig(png_path, dpi=180)
  fig.savefig(pdf_path)
  plt.close(fig)
  return True


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(description="Audit Songling's cyclic 3-edge-cut Kempe-chain request.")
  parser.add_argument("--orders", nargs="+", type=int, default=[13, 15, 17, 19])
  parser.add_argument("--min-h-order", type=int, default=5, help="Only test H components with at least this many vertices.")
  parser.add_argument("--json-output", type=Path, default=REPORTS_DIR / "songling_cyclic3_kempe_chain_hmin5_audit_20260530.json")
  parser.add_argument("--md-output", type=Path, default=REPORTS_DIR / "songling_cyclic3_kempe_chain_hmin5_audit_20260530.md")
  parser.add_argument("--counterexample-png", type=Path, default=ASSETS_DIR / "songling-cyclic3-kempe-hmin5-counterexample-20260530.png")
  parser.add_argument("--counterexample-pdf", type=Path, default=ASSETS_DIR / "songling-cyclic3-kempe-hmin5-counterexample-20260530.pdf")
  parser.add_argument("--stop-on-first-fail", action="store_true")
  parser.add_argument("--keep-witnesses", action="store_true")
  args = parser.parse_args(argv)

  report = audit_orders(args.orders, min_h_order=args.min_h_order, stop_on_first_fail=args.stop_on_first_fail, keep_witnesses=args.keep_witnesses)
  args.json_output.parent.mkdir(parents=True, exist_ok=True)
  args.json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  write_markdown(report, args.md_output)
  plotted = plot_counterexample(report, args.counterexample_png, args.counterexample_pdf)
  print(json.dumps({
    "json_output": str(args.json_output),
    "md_output": str(args.md_output),
    "counterexample_png": str(args.counterexample_png) if plotted else None,
    "counterexample_pdf": str(args.counterexample_pdf) if plotted else None,
    "summary": report["summary"],
    "first_counterexample": None if report.get("first_counterexample") is None else {
      "order": report["first_counterexample"]["order"],
      "survivor_index": report["first_counterexample"]["survivor_index"],
      "failed_condition_count": report["first_counterexample"]["result"]["failed_condition_count"],
    },
  }, indent=2, sort_keys=True))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
