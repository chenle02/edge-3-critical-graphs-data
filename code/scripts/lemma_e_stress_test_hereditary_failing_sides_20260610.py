#!/usr/bin/python3
"""Lemma E stress test: exhaustive hunt for hereditarily failing tight sides.

Candidate Lemma E (A16): every nontrivial 3-critical graph in the Step-4 case
has at least one cyclic 3-edge-cut whose tight side admits a Delta-critical
simple boundary-pair completion.

Reduction.  Every qualifying tight side contains a MINIMAL qualifying tight
sub-side (finiteness of the containment order), so Lemma E follows if every
minimal side completes.  A counterexample to Lemma E therefore requires a
"hereditarily failing" side: a tight side with NO Delta-critical boundary-pair
completion such that every qualifying tight sub-side also has none.  The known
A13 order-15 failing side is NOT such a seed: it contains the order-7 sub-side
`FsOig` whose completions are all critical (Route B, A16).

This script exhaustively enumerates all candidate tight sides of given odd
orders and hunts for hereditarily failing ones.

Candidate side = connected simple graph, degree sequence 3^{n-3} 2^3
(forced by fixing m = (3n-3)/2 in geng with 2 <= deg <= 3), which is the
shape of any tight cyclic-3-cut side.  Filters applied, with counts:

1. no cyclic edge cut smaller than 3 (a cyclic 1/2-cut inside the side would
   be one in the ambient G, excluded in the Step-4 case);
2. A is 3-edge-colorable (necessary: A sits inside G-e for an edge e of the
   opposite side, and G critical makes G-e colorable);
3. completion test (short-circuit): some non-edge boundary pair p with A+p
   Delta-critical -> side PASSES;
4. for failing sides only: local embeddability (every A-e 3-edge-colorable,
   also necessary for sides of a critical ambient graph) and hereditary
   analysis via the triangle-cap trick: the qualifying tight sub-sides of A
   inside ANY ambient graph are exactly the qualifying sides of the triangle
   cap T_A that avoid the three cap vertices (the cap supplies the cyclic
   opposite side that the ambient would supply).

Outcome semantics:
- zero hereditarily failing sides up to order N  ==>  any Lemma E
  counterexample must contain a failing MINIMAL side of order >= N+2; all
  known evidence (census orders 13-21, the order-25 obstruction) stays
  consistent with Lemma E.
- a hereditarily failing side is a counterexample SEED only; it still needs
  an ambient critical embedding (Phase 2 gluing) to refute Lemma E.

Guardrail: finite local evidence; not a theorem.  Do not send Songling-facing
prose from this audit without a fresh review/honesty gate.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parents[2]
CGS = REPO_ROOT / "codes" / "critical_graph_search"
sys.path.insert(0, str(CGS))
sys.path.insert(0, str(CGS / "scripts"))

from critical_graph_search.criticality import is_delta_critical  # noqa: E402
from critical_graph_search.edge_coloring import is_k_edge_colorable  # noqa: E402
import audit_songling_cyclic3_kempe_chain_request as kempe_audit  # noqa: E402

REPORTS_DIR = REPO_ROOT / ".hermes" / "reports"
KNOWN_A13_FAILING_SIDE_N15_CANONICAL = None  # filled at runtime for cross-check


def boundary_of(side: nx.Graph) -> list[int]:
  return sorted(int(v) for v, d in side.degree() if d == 2)


def completion_status(side: nx.Graph, boundary: list[int]) -> dict[str, Any]:
  """Short-circuit completion test.  Returns pass/fail plus per-pair detail."""
  pairs = [(boundary[0], boundary[1]), (boundary[0], boundary[2]), (boundary[1], boundary[2])]
  detail: list[dict[str, Any]] = []
  has_critical = False
  for u, v in pairs:
    if side.has_edge(u, v):
      detail.append({"pair": [u, v], "already_edge": True})
      continue
    completed = side.copy()
    completed.add_edge(u, v)
    if is_k_edge_colorable(completed, 3):
      detail.append({"pair": [u, v], "already_edge": False, "colorable": True, "is_delta_critical": False})
      continue
    critical = bool(is_delta_critical(completed))
    detail.append({"pair": [u, v], "already_edge": False, "colorable": False, "is_delta_critical": critical})
    if critical:
      has_critical = True
      break
  return {"has_delta_critical_completion": has_critical, "pairs": detail}


def all_single_deletions_colorable(side: nx.Graph) -> bool:
  for edge in list(side.edges()):
    pruned = side.copy()
    pruned.remove_edge(*edge)
    if not is_k_edge_colorable(pruned, 3):
      return False
  return True


def qualifying_subsides_via_triangle_cap(side: nx.Graph, boundary: list[int], *, min_h_order: int = 5) -> list[dict[str, Any]]:
  """Ambient-independent qualifying tight sub-sides of `side`.

  Build the triangle cap T_A (cap vertices get degree 3, the cap triangle is a
  cycle, so T_A is cubic and the original side itself shows up as the
  qualifying side across the cap cut).  The qualifying sides of T_A that avoid
  the cap vertices are exactly the tight sub-sides `side` would present inside
  any ambient graph.  The full side itself is excluded (proper sub-sides only).
  """
  capped = side.copy()
  base = max(capped.nodes()) + 1
  caps = [base, base + 1, base + 2]
  capped.add_edges_from(zip(caps, boundary))
  capped.add_edges_from([(caps[0], caps[1]), (caps[1], caps[2]), (caps[0], caps[2])])
  cap_set = set(caps)
  side_vertices = set(side.nodes())
  records = []
  for rec in kempe_audit.iter_qualifying_h_components(capped, min_h_order=min_h_order):
    comp = set(rec["component_vertices_in_G"])
    if comp & cap_set:
      continue
    if comp == side_vertices:
      continue
    records.append(rec)
  return records


def analyze_failing_side(side: nx.Graph, boundary: list[int]) -> dict[str, Any]:
  embeddable = all_single_deletions_colorable(side)
  subsides = qualifying_subsides_via_triangle_cap(side, boundary)
  sub_records: list[dict[str, Any]] = []
  any_subside_completes = False
  for rec in subsides:
    sub = rec["h"]
    sub_boundary = sorted(int(v) for v in rec["boundary_vertices_in_G"])
    status = completion_status(sub, sub_boundary)
    sub_records.append({
      "subside_order": sub.number_of_nodes(),
      "subside_graph6": kempe_audit.graph6_string(sub),
      "boundary": sub_boundary,
      "has_delta_critical_completion": status["has_delta_critical_completion"],
    })
    if status["has_delta_critical_completion"]:
      any_subside_completes = True
  return {
    "locally_embeddable_all_deletions_colorable": embeddable,
    "qualifying_proper_subsides": len(sub_records),
    "subsides": sub_records,
    "some_subside_completes": any_subside_completes,
    "hereditarily_failing": embeddable and not any_subside_completes,
  }


def run_order(n: int, geng_path: str, *, log_every: int = 100000) -> dict[str, Any]:
  m = (3 * n - 3) // 2
  cmd = [geng_path, "-c", "-d2", "-D3", "-q", str(n), f"{m}:{m}"]
  stats = {
    "n": n,
    "m": m,
    "geng_command": " ".join(cmd),
    "candidates": 0,
    "skipped_cyclic_cut_lt3": 0,
    "skipped_side_not_colorable": 0,
    "sides_with_critical_completion": 0,
    "failing_sides": 0,
    "failing_not_locally_embeddable": 0,
    "failing_rescued_by_subside": 0,
    "hereditarily_failing": 0,
  }
  failing_records: list[dict[str, Any]] = []
  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
  assert proc.stdout is not None
  for line in proc.stdout:
    g6 = line.strip()
    if not g6:
      continue
    stats["candidates"] += 1
    if stats["candidates"] % log_every == 0:
      print(f"[order {n}] processed {stats['candidates']} candidates...", flush=True)
    side = nx.from_graph6_bytes(g6.encode())
    if kempe_audit.has_cyclic_edge_cut_smaller_than_3(side):
      stats["skipped_cyclic_cut_lt3"] += 1
      continue
    if not is_k_edge_colorable(side, 3):
      stats["skipped_side_not_colorable"] += 1
      continue
    boundary = boundary_of(side)
    status = completion_status(side, boundary)
    if status["has_delta_critical_completion"]:
      stats["sides_with_critical_completion"] += 1
      continue
    stats["failing_sides"] += 1
    analysis = analyze_failing_side(side, boundary)
    if not analysis["locally_embeddable_all_deletions_colorable"]:
      stats["failing_not_locally_embeddable"] += 1
    elif analysis["some_subside_completes"]:
      stats["failing_rescued_by_subside"] += 1
    if analysis["hereditarily_failing"]:
      stats["hereditarily_failing"] += 1
      print(f"[order {n}] HEREDITARILY FAILING side found: {g6}", flush=True)
    failing_records.append({
      "graph6": g6,
      "boundary": boundary,
      "completion_pairs": status["pairs"],
      **analysis,
    })
  proc.wait()
  if proc.returncode != 0:
    raise RuntimeError(f"geng exited with {proc.returncode} for order {n}")
  return {"stats": stats, "failing_records": failing_records}


def main() -> int:
  parser = argparse.ArgumentParser(description="Lemma E stress test: hereditary failing tight-side hunt")
  parser.add_argument("--orders", nargs="+", type=int, default=[7, 9, 11, 13, 15])
  parser.add_argument("--geng-path", default="/usr/bin/geng")
  args = parser.parse_args()

  by_order: dict[str, Any] = {}
  all_failing: list[dict[str, Any]] = []
  total_hereditary = 0
  for n in args.orders:
    if n % 2 == 0:
      raise ValueError("tight sides have odd order; even order requested")
    result = run_order(n, args.geng_path)
    by_order[str(n)] = result["stats"]
    for rec in result["failing_records"]:
      rec["order"] = n
      all_failing.append(rec)
    total_hereditary += result["stats"]["hereditarily_failing"]

  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  max_order = max(args.orders)
  report = {
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "question": (
      "Does a hereditarily failing tight side (no Delta-critical boundary-pair "
      "completion, and none for any qualifying tight sub-side, locally "
      "embeddable) exist at the tested orders?  Such a side is the necessary "
      "seed of any Lemma E counterexample."
    ),
    "parameters": {"orders": args.orders, "geng": args.geng_path},
    "summary": {
      "orders_tested_exhaustively": args.orders,
      "total_candidates": sum(s["candidates"] for s in by_order.values()),
      "total_failing_sides": sum(s["failing_sides"] for s in by_order.values()),
      "total_hereditarily_failing": total_hereditary,
      "lemma_e_seed_found": total_hereditary > 0,
      "conclusion_if_zero": (
        f"any Lemma E counterexample must contain a failing minimal tight side "
        f"of order >= {max_order + 2}"
      ),
      "scope_caveat": (
        "exhaustive finite enumeration of tight-side shapes at the tested "
        "orders under the implemented conventions; not an all-order theorem"
      ),
    },
    "by_order": by_order,
    "failing_sides": all_failing,
  }
  json_path = REPORTS_DIR / f"lemma_e_stress_test_hereditary_failing_sides_{timestamp}.json"
  json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

  lines = [
    "# Lemma E stress test: exhaustive hereditary failing tight-side hunt",
    "",
    f"Generated: {report['generated_at']}",
    "",
    "## Question",
    "A Lemma E counterexample needs a hereditarily failing tight side (the side",
    "and ALL its qualifying tight sub-sides lack Delta-critical boundary-pair",
    "completions, and the side passes the local embeddability conditions).",
    "This run enumerates ALL tight-side shapes (degree sequence 3^{n-3} 2^3,",
    "connected, no cyclic cut < 3) at the tested orders via geng — exhaustive,",
    "unlike the random A13 probes (~3,400 sides/order).",
    "",
    "## Summary",
    f"- Orders (exhaustive): {args.orders}",
    f"- Total candidates: {report['summary']['total_candidates']}",
    f"- Failing sides (no critical completion): {report['summary']['total_failing_sides']}",
    f"- **Hereditarily failing sides (Lemma E seeds): {total_hereditary}**",
  ]
  if total_hereditary == 0:
    lines.append(f"- Conclusion: {report['summary']['conclusion_if_zero']}.")
  lines.extend(["", "## By order", ""])
  lines.append("| n | candidates | cyclic-cut<3 skip | not colorable | completes | failing | not embeddable | rescued by sub-side | HEREDITARY |")
  lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
  for order, s in sorted(by_order.items(), key=lambda kv: int(kv[0])):
    lines.append(
      f"| {order} | {s['candidates']} | {s['skipped_cyclic_cut_lt3']} | "
      f"{s['skipped_side_not_colorable']} | {s['sides_with_critical_completion']} | "
      f"{s['failing_sides']} | {s['failing_not_locally_embeddable']} | "
      f"{s['failing_rescued_by_subside']} | {s['hereditarily_failing']} |"
    )
  if all_failing:
    lines.extend(["", "## Failing sides detail", ""])
    for rec in all_failing:
      lines.append(
        f"- order {rec['order']}, `{rec['graph6']}`: embeddable="
        f"{rec['locally_embeddable_all_deletions_colorable']}, "
        f"sub-sides={rec['qualifying_proper_subsides']}, "
        f"some sub-side completes={rec['some_subside_completes']}, "
        f"HEREDITARY={rec['hereditarily_failing']}"
      )
  lines.extend([
    "",
    "## Guardrails",
    "- Finite exhaustive local evidence; not an all-order theorem.",
    "- A hereditarily failing side is only a counterexample SEED; refuting",
    "  Lemma E additionally requires an ambient critical embedding.",
    "- Do not send Songling-facing prose from this audit without a fresh gate.",
    "",
    f"JSON sibling: `{json_path.name}`",
  ])
  md_path = REPORTS_DIR / f"lemma_e_stress_test_hereditary_failing_sides_{timestamp}.md"
  md_path.write_text("\n".join(lines) + "\n")
  print("\n".join(lines))
  print(f"\nwritten: {json_path}\nwritten: {md_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
