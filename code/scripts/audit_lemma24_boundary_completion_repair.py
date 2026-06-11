#!/usr/bin/python3
from __future__ import annotations

import argparse
import collections
import gzip
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
RESULTS_DIR = ROOT / "results"
REPORTS_DIR = REPO_ROOT / ".hermes" / "reports"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

from critical_graph_search.criticality import is_delta_critical  # noqa: E402
import audit_songling_cyclic3_kempe_chain_request as kempe_audit  # noqa: E402

Edge = tuple[int, int]


def norm_pair(pair: tuple[int, int] | list[int]) -> Edge:
  u, v = int(pair[0]), int(pair[1])
  return (u, v) if u < v else (v, u)


def load_order(order: int) -> dict[str, Any]:
  plain = RESULTS_DIR / f"order_{order}_delta_3.json"
  gz = RESULTS_DIR / f"order_{order}_delta_3.json.gz"
  if plain.exists():
    data = json.loads(plain.read_text())
    source_path = plain
  elif gz.exists():
    with gzip.open(gz, "rt") as handle:
      data = json.load(handle)
    source_path = gz
  else:
    raise FileNotFoundError(f"no order-{order} delta-3 result JSON found")
  survivors = data.get("survivors", [])
  if data.get("survivor_count") != len(survivors):
    raise ValueError(f"order {order} survivor_count mismatch in {source_path}")
  if data.get("interrupted") is True:
    raise ValueError(f"order {order} source is marked interrupted: {source_path}")
  data["_source_path"] = str(source_path.relative_to(REPO_ROOT))
  return data


def evaluate_boundary_pair_completions(h: nx.Graph, boundary: list[int]) -> list[dict[str, Any]]:
  """Test simple boundary-pair completions A+a_i a_j for one boundary-first side.

  Existing boundary edges are recorded but do not count as valid simple added-edge
  completions.  Non-existing pairs are completed in a simple graph and tested by
  the repo's Delta-critical predicate.
  """
  results: list[dict[str, Any]] = []
  for raw_pair in ((0, 1), (0, 2), (1, 2)):
    pair = norm_pair(raw_pair)
    if pair[0] not in boundary or pair[1] not in boundary:
      raise ValueError(f"boundary pair {pair} is not contained in boundary {boundary}")
    if h.has_edge(*pair):
      results.append({
        "pair": list(pair),
        "already_edge": True,
        "completion_graph6": None,
        "is_delta_critical": None,
      })
      continue
    completed = h.copy()
    completed.add_edge(*pair)
    results.append({
      "pair": list(pair),
      "already_edge": False,
      "completion_graph6": kempe_audit.graph6_string(completed),
      "is_delta_critical": bool(is_delta_critical(completed)),
    })
  return results


def audit_survivor(order: int, survivor_index: int, survivor: dict[str, Any], *, min_h_order: int) -> list[dict[str, Any]]:
  graph = kempe_audit.graph_from_survivor(survivor)
  records: list[dict[str, Any]] = []
  for h_record in kempe_audit.iter_qualifying_h_components(graph, min_h_order=min_h_order):
    h, boundary, mapping = kempe_audit.relabel_h_boundary_first(
      h_record["h"], h_record["boundary_vertices_in_G"]
    )
    inverse_mapping = {new: old for old, new in mapping.items()}
    completions = evaluate_boundary_pair_completions(h, boundary)
    positive_nonedge_pairs = [
      item["pair"]
      for item in completions
      if item["already_edge"] is False and item["is_delta_critical"] is True
    ]
    records.append({
      "order": order,
      "survivor_index": survivor_index,
      "survivor_graph6": survivor.get("graph6"),
      "cut_edges": h_record["cut_edges"],
      "component_vertices_in_G": h_record["component_vertices_in_G"],
      "boundary_vertices_in_G": h_record["boundary_vertices_in_G"],
      "boundary_label_to_vertex_in_G": {str(label): inverse_mapping[label] for label in boundary},
      "h_graph6_boundary_first": kempe_audit.graph6_string(h),
      "h_node_count": h.number_of_nodes(),
      "h_edge_count": h.number_of_edges(),
      "boundary_pair_completions": completions,
      "positive_nonedge_pairs": positive_nonedge_pairs,
      "has_delta_critical_boundary_pair_completion": bool(positive_nonedge_pairs),
    })
  return records


def audit_orders(
  orders: list[int],
  *,
  min_h_order: int = 5,
  stop_at_first_failure: bool = False,
  write_reports: bool = True,
  report_stem: str = "lemma24_boundary_completion_census_audit",
) -> dict[str, Any]:
  tested_components: list[dict[str, Any]] = []
  by_order: dict[str, Any] = {}
  first_failure: dict[str, Any] | None = None
  sources: dict[str, str] = {}

  for order in orders:
    data = load_order(order)
    sources[str(order)] = data["_source_path"]
    order_stats = {
      "source_survivor_count": len(data["survivors"]),
      "skipped_not_cyclically_3_edge_connected": 0,
      "graphs_with_qualifying_h": 0,
      "qualifying_h_components": 0,
      "components_with_delta_critical_boundary_pair_completion": 0,
      "components_without_delta_critical_boundary_pair_completion": 0,
      "positive_nonedge_pair_count_distribution": {},
    }
    distribution: collections.Counter[int] = collections.Counter()

    for survivor_index, survivor in enumerate(data["survivors"], start=1):
      graph = kempe_audit.graph_from_survivor(survivor)
      if kempe_audit.has_cyclic_edge_cut_smaller_than_3(graph):
        order_stats["skipped_not_cyclically_3_edge_connected"] += 1
        continue
      records = audit_survivor(order, survivor_index, survivor, min_h_order=min_h_order)
      if records:
        order_stats["graphs_with_qualifying_h"] += 1
      for record in records:
        tested_components.append(record)
        order_stats["qualifying_h_components"] += 1
        positive_count = len(record["positive_nonedge_pairs"])
        distribution[positive_count] += 1
        if record["has_delta_critical_boundary_pair_completion"]:
          order_stats["components_with_delta_critical_boundary_pair_completion"] += 1
        else:
          order_stats["components_without_delta_critical_boundary_pair_completion"] += 1
          if first_failure is None:
            first_failure = record
          if stop_at_first_failure:
            order_stats["positive_nonedge_pair_count_distribution"] = {
              str(key): value for key, value in sorted(distribution.items())
            }
            by_order[str(order)] = order_stats
            return finish_report(
              orders, min_h_order, sources, tested_components, first_failure, by_order, write_reports, report_stem
            )

    order_stats["positive_nonedge_pair_count_distribution"] = {
      str(key): value for key, value in sorted(distribution.items())
    }
    by_order[str(order)] = order_stats

  return finish_report(orders, min_h_order, sources, tested_components, first_failure, by_order, write_reports, report_stem)


def finish_report(
  orders: list[int],
  min_h_order: int,
  sources: dict[str, str],
  tested_components: list[dict[str, Any]],
  first_failure: dict[str, Any] | None,
  by_order: dict[str, Any],
  write_reports: bool,
  report_stem: str,
) -> dict[str, Any]:
  failure_count = sum(1 for item in tested_components if not item["has_delta_critical_boundary_pair_completion"])
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  report = {
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "summary": {
      "orders": orders,
      "min_h_order": min_h_order,
      "qualifying_h_components_tested": len(tested_components),
      "components_without_delta_critical_boundary_pair_completion": failure_count,
      "all_tested_h_have_delta_critical_boundary_pair_completion": failure_count == 0,
      "early_stop": first_failure is not None and failure_count > 0,
      "scope_caveat": "finite census audit of the implemented simple boundary-pair completion condition; not a proof for unaudited conventions",
    },
    "sources": sources,
    "by_order": by_order,
    "first_failure": first_failure,
    "tested_components": tested_components,
  }
  if write_reports:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / f"{report_stem}_{timestamp}.json"
    md_path = REPORTS_DIR / f"{report_stem}_{timestamp}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(render_markdown(report) + "\n")
    report["written_paths"] = [str(json_path.relative_to(REPO_ROOT)), str(md_path.relative_to(REPO_ROOT))]
  return report


def render_markdown(report: dict[str, Any]) -> str:
  lines = [
    "# Lemma 2.4 boundary-pair completion census audit",
    "",
    f"Generated: {report['generated_at']}",
    "",
    "## Scope",
    f"- Orders tested: {report['summary']['orders']}",
    f"- Minimum component order: {report['summary']['min_h_order']}",
    "- For each qualifying cyclic-3-cut side `H`, relabel the three boundary degree-2 vertices as `0,1,2`.",
    "- For each non-existing boundary pair, add the simple edge and test whether the completion is Delta-critical.",
    "- Existing boundary edges are recorded as `already_edge` and are not counted as added-edge completions.",
    "- Guardrail: do not send Songling-facing prose from this audit without a fresh review/honesty gate.",
    "- Caveat: this is a finite audit of the implemented simple boundary-pair completion condition, not a theorem for unaudited conventions.",
    "",
    "## Summary",
    f"- Qualifying H components tested: {report['summary']['qualifying_h_components_tested']}",
    "- Components without a Delta-critical boundary-pair completion: "
    f"{report['summary']['components_without_delta_critical_boundary_pair_completion']}",
    "- All tested H have a Delta-critical boundary-pair completion: "
    f"{report['summary']['all_tested_h_have_delta_critical_boundary_pair_completion']}",
    f"- Early stop: {report['summary']['early_stop']}",
    "",
    "## Sources",
  ]
  for order, source in sorted(report["sources"].items(), key=lambda item: int(item[0])):
    lines.append(f"- Order {order}: `{source}`")
  lines.append("")
  lines.append("## By order")
  for order, stats in sorted(report["by_order"].items(), key=lambda item: int(item[0])):
    lines.extend([
      "",
      f"### Order {order}",
      f"- Source survivor count: {stats['source_survivor_count']}",
      f"- Skipped because not cyclically 3-edge-connected: {stats['skipped_not_cyclically_3_edge_connected']}",
      f"- Graphs with qualifying H: {stats['graphs_with_qualifying_h']}",
      f"- Qualifying H components: {stats['qualifying_h_components']}",
      "- Components with a Delta-critical boundary-pair completion: "
      f"{stats['components_with_delta_critical_boundary_pair_completion']}",
      "- Components without a Delta-critical boundary-pair completion: "
      f"{stats['components_without_delta_critical_boundary_pair_completion']}",
      "- Positive non-edge pair count distribution: "
      f"{stats['positive_nonedge_pair_count_distribution']}",
    ])
  if report.get("first_failure"):
    failure = report["first_failure"]
    lines.extend([
      "",
      "## First failure",
      f"- Order: {failure['order']}",
      f"- Survivor index: {failure['survivor_index']}",
      f"- Boundary-first H graph6: `{failure['h_graph6_boundary_first']}`",
      f"- Cut edges: {failure['cut_edges']}",
    ])
  return "\n".join(lines)


def main() -> None:
  parser = argparse.ArgumentParser(description="Audit the Lemma 2.4 critical boundary-pair completion repair condition.")
  parser.add_argument("--orders", nargs="+", type=int, default=[13, 15, 17, 19])
  parser.add_argument("--min-h-order", type=int, default=5)
  parser.add_argument("--stop-at-first-failure", action="store_true")
  parser.add_argument("--no-write-reports", action="store_true")
  args = parser.parse_args()
  report = audit_orders(
    args.orders,
    min_h_order=args.min_h_order,
    stop_at_first_failure=args.stop_at_first_failure,
    write_reports=not args.no_write_reports,
  )
  print(render_markdown(report))


if __name__ == "__main__":
  main()
