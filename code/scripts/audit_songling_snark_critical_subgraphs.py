#!/usr/bin/python3
from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent.parent
PKG_ROOT = ROOT
if str(PKG_ROOT) not in sys.path:
  sys.path.insert(0, str(PKG_ROOT))

from critical_graph_search.edge_coloring import is_class2, is_k_edge_colorable

REPORTS_DIR = REPO_ROOT / ".hermes" / "reports"
PRIOR_SNARK_AUDIT = REPORTS_DIR / "songling_followup_snark_deletion_audit.json"
DEFAULT_JSON_OUTPUT = REPORTS_DIR / "songling_snark_critical_subgraph_audit.json"
DEFAULT_MD_OUTPUT = REPORTS_DIR / "songling_snark_critical_subgraph_audit.md"
DEFAULT_CSV_OUTPUT = REPORTS_DIR / "songling_snark_critical_subgraph_audit.csv"


@dataclass(frozen=True)
class SnarkClass:
  family: str
  order: int
  class_index: int
  graph6: str
  source_indices: list[int]
  convention: str


def graph_from_graph6(graph6: str) -> nx.Graph:
  return nx.from_graph6_bytes(graph6.encode("ascii"))


def graph6_string(graph: nx.Graph) -> str:
  normalized = nx.convert_node_labels_to_integers(graph, ordering="sorted")
  return nx.to_graph6_bytes(normalized, header=False).decode("ascii").strip()


def girth(graph: nx.Graph) -> int | None:
  best: int | None = None
  for source in graph.nodes():
    distances = {source: 0}
    parents = {source: None}
    queue = [source]
    for vertex in queue:
      for neighbor in graph.neighbors(vertex):
        if neighbor not in distances:
          distances[neighbor] = distances[vertex] + 1
          parents[neighbor] = vertex
          queue.append(neighbor)
        elif parents[vertex] != neighbor and parents[neighbor] != vertex:
          candidate = distances[vertex] + distances[neighbor] + 1
          if best is None or candidate < best:
            best = candidate
  return best


def is_delta_critical_with_impl(graph: nx.Graph, implementation: str) -> bool:
  """Dual-checkable Δ-critical test for small simple graphs."""
  if graph.number_of_edges() == 0:
    return False
  if not nx.is_connected(graph):
    return False
  if any(degree < 2 for _, degree in graph.degree()):
    return False
  if any(nx.bridges(graph)):
    return False
  delta = max(degree for _, degree in graph.degree())
  if delta != 3:
    return False
  if not is_class2(graph, implementation=implementation):
    return False
  for u, v in graph.edges():
    reduced = graph.copy()
    reduced.remove_edge(u, v)
    if not is_k_edge_colorable(reduced, delta, implementation=implementation):
      return False
  return True


def criticality_record(graph: nx.Graph) -> dict[str, Any]:
  fast = is_delta_critical_with_impl(graph, "fast")
  reference = is_delta_critical_with_impl(graph, "reference")
  return {
    "fast_delta_critical": fast,
    "reference_delta_critical": reference,
    "dual_checker_positive": bool(fast and reference),
  }


def load_standard_snark_classes(path: Path = PRIOR_SNARK_AUDIT) -> list[SnarkClass]:
  """Load strict/common snark isomorphism classes from the previous verified audit."""
  with path.open(encoding="utf-8") as handle:
    prior = json.load(handle)
  classes: list[SnarkClass] = []
  for family_key, order, family in [
    ("order17_girth5_remaining", 18, "order18_from_order17_deletions"),
    ("order19_remaining", 20, "order20_from_order19_deletions"),
  ]:
    for item in prior[family_key]["strict_candidate_snark_iso_classes"]:
      classes.append(
        SnarkClass(
          family=family,
          order=order,
          class_index=int(item["class_index"]),
          graph6=item["completion_graph6"],
          source_indices=[int(value) for value in item["source_indices"]],
          convention="strict/common: weak snark, girth >= 5, no cyclic edge-cut of size 1, 2, or 3",
        )
      )
  return classes


def survivor_result_path(order: int) -> Path:
  delta_path = ROOT / "results" / f"order_{order}_delta_3.json"
  if delta_path.exists():
    return delta_path
  return ROOT / "results" / f"order_{order}.json"


def invariant_key(graph: nx.Graph) -> tuple[Any, ...]:
  degree_values = tuple(sorted(degree for _, degree in graph.degree()))
  triangles = sum(nx.triangles(graph).values()) // 3
  return (graph.number_of_nodes(), graph.number_of_edges(), degree_values, triangles, girth(graph))


def load_census_by_order(orders: set[int]) -> dict[int, dict[tuple[Any, ...], list[dict[str, Any]]]]:
  buckets: dict[int, dict[tuple[Any, ...], list[dict[str, Any]]]] = {}
  for order in sorted(orders):
    path = survivor_result_path(order)
    with path.open(encoding="utf-8") as handle:
      data = json.load(handle)
    if data.get("survivor_count") != len(data.get("survivors", [])):
      raise RuntimeError(f"Survivor count mismatch in {path}")
    order_buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(data["survivors"], start=1):
      graph = graph_from_graph6(row["graph6"])
      order_buckets[invariant_key(graph)].append({"index": index, "graph6": row["graph6"], "graph": graph})
    buckets[order] = order_buckets
  return buckets


def census_matches(graph: nx.Graph, census: dict[int, dict[tuple[Any, ...], list[dict[str, Any]]]]) -> list[dict[str, Any]]:
  order = graph.number_of_nodes()
  key = invariant_key(graph)
  matches: list[dict[str, Any]] = []
  for candidate in census.get(order, {}).get(key, []):
    if nx.is_isomorphic(graph, candidate["graph"]):
      matches.append({"index": candidate["index"], "graph6": candidate["graph6"]})
  return matches


def snark_classification(graph: nx.Graph) -> dict[str, Any]:
  is_cubic = all(degree == 3 for _, degree in graph.degree())
  is_connected = nx.is_connected(graph)
  bridge_count = len(list(nx.bridges(graph))) if is_connected else None
  completion_girth = girth(graph)
  fast_class2 = is_class2(graph, implementation="fast")
  reference_class2 = is_class2(graph, implementation="reference")
  cyclic_cut_note = "inherited from prior strict/common snark audit; not recomputed in this focused subgraph script"
  return {
    "is_cubic": is_cubic,
    "is_connected": is_connected,
    "bridge_count": bridge_count,
    "girth": completion_girth,
    "fast_class2": fast_class2,
    "reference_class2": reference_class2,
    "cyclic_cut_note": cyclic_cut_note,
  }


def enumerate_critical_subgraphs_for_snark(snark: SnarkClass, census: dict[int, dict[tuple[Any, ...], list[dict[str, Any]]]]) -> dict[str, Any]:
  source = graph_from_graph6(snark.graph6)
  raw_records: list[dict[str, Any]] = []

  for deleted_vertex in sorted(source.nodes()):
    vertex_deleted = source.copy()
    vertex_deleted.remove_node(deleted_vertex)
    vertex_deleted = nx.convert_node_labels_to_integers(vertex_deleted, ordering="sorted")
    crit = criticality_record(vertex_deleted)
    if crit["dual_checker_positive"]:
      raw_records.append(
        {
          "operation": "delete_vertex",
          "deleted_vertex": int(deleted_vertex),
          "deleted_edge_after_vertex_deletion": None,
          "graph6": graph6_string(vertex_deleted),
          "node_count": vertex_deleted.number_of_nodes(),
          "edge_count": vertex_deleted.number_of_edges(),
          "degree2_count": sum(1 for _, degree in vertex_deleted.degree() if degree == 2),
          "degree_sequence": sorted(degree for _, degree in vertex_deleted.degree()),
          "girth": girth(vertex_deleted),
          "census_matches": census_matches(vertex_deleted, census),
          **crit,
        }
      )

    # Also test the first non-induced strengthening: after deleting one vertex,
    # remove one additional remaining edge.  The final order-17/order-19 census
    # has only degree-2 counts 3 and 5, so this catches the possible same-order
    # critical subgraphs not equal to a pure vertex deletion.
    vertex_deleted_original_labels = source.copy()
    vertex_deleted_original_labels.remove_node(deleted_vertex)
    for edge in sorted(tuple(sorted((int(u), int(v)))) for u, v in vertex_deleted_original_labels.edges()):
      edge_deleted = vertex_deleted_original_labels.copy()
      edge_deleted.remove_edge(*edge)
      if any(degree < 2 for _, degree in edge_deleted.degree()):
        continue
      normalized = nx.convert_node_labels_to_integers(edge_deleted, ordering="sorted")
      crit_edge = criticality_record(normalized)
      if crit_edge["dual_checker_positive"]:
        raw_records.append(
          {
            "operation": "delete_vertex_then_edge",
            "deleted_vertex": int(deleted_vertex),
            "deleted_edge_after_vertex_deletion": [int(edge[0]), int(edge[1])],
            "graph6": graph6_string(normalized),
            "node_count": normalized.number_of_nodes(),
            "edge_count": normalized.number_of_edges(),
            "degree2_count": sum(1 for _, degree in normalized.degree() if degree == 2),
            "degree_sequence": sorted(degree for _, degree in normalized.degree()),
            "girth": girth(normalized),
            "census_matches": census_matches(normalized, census),
            **crit_edge,
          }
        )

  # Group the raw operation witnesses into isomorphism classes per snark.
  groups: list[dict[str, Any]] = []
  for record in raw_records:
    graph = graph_from_graph6(record["graph6"])
    for group in groups:
      if nx.is_isomorphic(graph, group["_graph"]):
        group["witnesses"].append({k: record[k] for k in ["operation", "deleted_vertex", "deleted_edge_after_vertex_deletion"]})
        group["operations"] = sorted(set(group["operations"] + [record["operation"]]))
        break
    else:
      groups.append(
        {
          "_graph": graph,
          "graph6": record["graph6"],
          "node_count": record["node_count"],
          "edge_count": record["edge_count"],
          "degree2_count": record["degree2_count"],
          "girth": record["girth"],
          "census_matches": record["census_matches"],
          "operations": [record["operation"]],
          "witnesses": [{k: record[k] for k in ["operation", "deleted_vertex", "deleted_edge_after_vertex_deletion"]}],
        }
      )
  for index, group in enumerate(groups, start=1):
    group["subgraph_class_index"] = index
    group["witness_count"] = len(group["witnesses"])
    del group["_graph"]

  operation_counts = Counter(record["operation"] for record in raw_records)
  non_vertex_records = [record for record in raw_records if record["operation"] != "delete_vertex"]
  missing_census = [record for record in raw_records if not record["census_matches"]]
  return {
    "snark": {
      "family": snark.family,
      "order": snark.order,
      "class_index": snark.class_index,
      "graph6": snark.graph6,
      "source_indices": snark.source_indices,
      "convention": snark.convention,
      **snark_classification(source),
    },
    "summary": {
      "critical_subgraph_witness_count": len(raw_records),
      "critical_subgraph_iso_class_count": len(groups),
      "operation_counts": dict(sorted(operation_counts.items())),
      "has_non_vertex_deletion_critical_subgraph": bool(non_vertex_records),
      "non_vertex_deletion_witness_count": len(non_vertex_records),
      "missing_census_match_count": len(missing_census),
    },
    "critical_subgraph_classes": groups,
    "raw_witnesses": raw_records,
  }


def markdown_code(text: object) -> str:
  value = str(text)
  if "`" not in value:
    return f"`{value}`"
  return f"``{value}``"


def render_markdown(report: dict[str, Any]) -> str:
  lines = [
    "# Songling snark critical-subgraph audit",
    "",
    "## Request and scope",
    "",
    "Songling's 2026-05-05 follow-up asks us to verify that the edge-chromatic 3-critical subgraphs of each snark of order 18 or 20 are obtained by deleting a vertex, and to list all possible such subgraphs and how they are obtained.",
    "",
    "This script audits the strict/common snark isomorphism classes already certified in `.hermes/reports/songling_followup_snark_deletion_audit.json`: the two order-18 classes and the six order-20 classes.  A graph is counted as edge-chromatic 3-critical only when both local edge-coloring implementations positively confirm `Δ`-criticality.",
    "",
    "Important scope note: the script tests all pure one-vertex deletions and also the first non-induced strengthening, one vertex plus one additional edge deletion.  This is enough to find concrete counterexamples to the literal non-induced-subgraph reading.  It is not a brute-force enumeration of every smaller arbitrary edge subset of a snark.",
    "",
    "## Top-level conclusion",
    "",
  ]
  summary = report["summary"]
  if summary["total_non_vertex_deletion_witness_count"]:
    lines.extend(
      [
        "Under the literal non-induced-subgraph reading, the proposed statement is **false** for the audited classes: there are edge-chromatic 3-critical subgraphs obtained by deleting one vertex and then one additional edge.",
        "",
        f"- Strict/common snark classes audited: `{summary['snark_class_count']}`",
        f"- Pure vertex-deletion critical raw witnesses: `{summary['total_vertex_deletion_witness_count']}`",
        f"- Vertex-plus-edge critical raw witnesses (not necessarily distinct isomorphism classes): `{summary['total_non_vertex_deletion_witness_count']}`",
        f"- Snark classes with at least one vertex-plus-edge counterexample: `{summary['snark_classes_with_non_vertex_counterexamples']}`",
        "",
        "If Songling intended **induced** subgraphs or specifically the previously studied order-17/order-19 residue graphs obtained as `S-v`, then the pure vertex-deletion lists below give the requested witnesses.  But the word `subgraph` should be qualified before promoting the statement to proof prose.",
      ]
    )
  else:
    lines.append("No non-vertex-deletion critical subgraph was found in the audited one-vertex plus optional one-edge search.")
  lines.extend(["", "## Per-snark counts", ""])
  for item in report["snark_audits"]:
    snark = item["snark"]
    counts = item["summary"]["operation_counts"]
    lines.extend(
      [
        f"### Order {snark['order']} strict/common class {snark['class_index']}",
        "",
        f"- Source deletion-residue indices from prior audit: `{snark['source_indices']}`",
        f"- Completion graph6: {markdown_code(snark['graph6'])}",
        f"- Pure vertex-deletion critical witnesses: `{counts.get('delete_vertex', 0)}`",
        f"- Vertex-plus-edge critical witnesses: `{counts.get('delete_vertex_then_edge', 0)}`",
        f"- Critical-subgraph isomorphism classes found: `{item['summary']['critical_subgraph_iso_class_count']}`",
        "",
      ]
    )
    vertex_ops = [record for record in item["raw_witnesses"] if record["operation"] == "delete_vertex"]
    edge_ops = [record for record in item["raw_witnesses"] if record["operation"] == "delete_vertex_then_edge"]
    lines.append("Pure vertex-deletion witnesses:")
    for record in vertex_ops:
      matches = [match["index"] for match in record["census_matches"]]
      lines.append(f"- delete vertex `{record['deleted_vertex']}` -> order-{record['node_count']} critical graph, census matches `{matches}`, graph6 {markdown_code(record['graph6'])}")
    if edge_ops:
      lines.extend(["", "Vertex-plus-edge critical witnesses (counterexamples to the literal non-induced wording):"])
      for record in edge_ops:
        matches = [match["index"] for match in record["census_matches"]]
        lines.append(f"- delete vertex `{record['deleted_vertex']}`, then edge `{record['deleted_edge_after_vertex_deletion']}` -> order-{record['node_count']} critical graph, census matches `{matches}`, graph6 {markdown_code(record['graph6'])}")
    lines.append("")
  lines.extend(
    [
      "## Conservative wording recommendation",
      "",
      "Do not write that all edge-chromatic 3-critical subgraphs of these snarks are obtained by deleting a vertex unless `subgraph` is explicitly restricted (for example to the intended induced/vertex-deletion residue).  The audited data supports the safer statement: the listed pure vertex deletions are edge-chromatic 3-critical; however, under ordinary non-induced subgraph terminology, additional 3-critical subgraphs appear after deleting one more edge.",
    ]
  )
  return "\n".join(lines) + "\n"


def write_csv(report: dict[str, Any], path: Path) -> None:
  fields = [
    "snark_order",
    "snark_class_index",
    "snark_graph6",
    "operation",
    "deleted_vertex",
    "deleted_edge_after_vertex_deletion",
    "subgraph_graph6",
    "node_count",
    "edge_count",
    "degree2_count",
    "girth",
    "census_match_indices",
  ]
  path.parent.mkdir(parents=True, exist_ok=True)
  with path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for item in report["snark_audits"]:
      snark = item["snark"]
      for record in item["raw_witnesses"]:
        writer.writerow(
          {
            "snark_order": snark["order"],
            "snark_class_index": snark["class_index"],
            "snark_graph6": snark["graph6"],
            "operation": record["operation"],
            "deleted_vertex": record["deleted_vertex"],
            "deleted_edge_after_vertex_deletion": record["deleted_edge_after_vertex_deletion"],
            "subgraph_graph6": record["graph6"],
            "node_count": record["node_count"],
            "edge_count": record["edge_count"],
            "degree2_count": record["degree2_count"],
            "girth": record["girth"],
            "census_match_indices": [match["index"] for match in record["census_matches"]],
          }
        )


def audit(json_output_path: Path = DEFAULT_JSON_OUTPUT, markdown_output_path: Path = DEFAULT_MD_OUTPUT, csv_output_path: Path = DEFAULT_CSV_OUTPUT) -> dict[str, Any]:
  snarks = load_standard_snark_classes()
  if len([snark for snark in snarks if snark.order == 18]) != 2:
    raise RuntimeError("Expected exactly two strict/common order-18 snark classes")
  if len([snark for snark in snarks if snark.order == 20]) != 6:
    raise RuntimeError("Expected exactly six strict/common order-20 snark classes")
  census = load_census_by_order({snark.order - 1 for snark in snarks})
  audits = [enumerate_critical_subgraphs_for_snark(snark, census) for snark in snarks]
  summary = {
    "snark_class_count": len(audits),
    "order18_snark_class_count": sum(1 for item in audits if item["snark"]["order"] == 18),
    "order20_snark_class_count": sum(1 for item in audits if item["snark"]["order"] == 20),
    "total_vertex_deletion_witness_count": sum(item["summary"]["operation_counts"].get("delete_vertex", 0) for item in audits),
    "total_non_vertex_deletion_witness_count": sum(item["summary"]["operation_counts"].get("delete_vertex_then_edge", 0) for item in audits),
    "snark_classes_with_non_vertex_counterexamples": sum(bool(item["summary"]["operation_counts"].get("delete_vertex_then_edge", 0)) for item in audits),
    "missing_census_match_count": sum(item["summary"]["missing_census_match_count"] for item in audits),
  }
  report = {
    "request": "Songling 2026-05-05: verify edge-chromatic 3-critical subgraphs of each order-18/order-20 snark, list all possible subgraphs found, and state how each is obtained.",
    "scope": {
      "snark_source": str(PRIOR_SNARK_AUDIT),
      "snark_convention": "strict/common classes from the prior audit: weak snark, girth >= 5, no cyclic edge-cut of size 1, 2, or 3",
      "subgraph_search": "all pure one-vertex deletions and all one-vertex-plus-one-edge deletions; dual edge-coloring checks for every positive 3-critical witness",
      "limitation": "not a brute-force enumeration of every smaller arbitrary edge subset; nevertheless, vertex-plus-edge positives already refute the literal non-induced statement",
    },
    "outputs": {"json": str(json_output_path), "markdown": str(markdown_output_path), "csv": str(csv_output_path)},
    "summary": summary,
    "snark_audits": audits,
  }
  if summary["missing_census_match_count"] != 0:
    raise RuntimeError(f"Some critical subgraph witnesses did not match the order n-1 census: {summary['missing_census_match_count']}")
  json_output_path.parent.mkdir(parents=True, exist_ok=True)
  json_output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
  markdown_output_path.write_text(render_markdown(report), encoding="utf-8")
  write_csv(report, csv_output_path)
  return report


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Audit critical subgraphs of the audited order-18/order-20 snark classes.")
  parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
  parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD_OUTPUT)
  parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
  return parser.parse_args()


def main() -> None:
  args = parse_args()
  report = audit(args.json_output, args.markdown_output, args.csv_output)
  print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
  main()
