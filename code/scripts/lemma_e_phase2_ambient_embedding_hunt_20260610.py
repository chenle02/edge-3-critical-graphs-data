#!/usr/bin/python3
"""Lemma E Phase 2: ambient embedding hunt for the hereditary failing seeds.

Phase 1 (A18) found 10 hereditarily failing tight sides at order 17: minimal
qualifying tight sides (zero qualifying proper sub-sides) with no
Delta-critical boundary-pair completion, passing the local embeddability
conditions.  Each is a Lemma E counterexample SEED.  This script hunts for an
actual counterexample: an ambient Delta-critical graph G containing a seed as
a qualifying tight side such that NO qualifying tight side of G admits a
Delta-critical boundary-pair completion.

Construction.  G = A  (seed, boundary b1,b2,b3 = its degree-2 vertices)
              + R  (complementary side, attachments a1,a2,a3)
              + cut edges {b_i a_{pi(i)}} over all 6 matchings pi.

Necessary conditions used as filters:
- R connected, contains a cycle (cyclic cut), max degree 3;
- attachments distinct, d_R(a_i) in {1,2}; every degree-1 vertex of R is an
  attachment (else G has a degree-1 vertex and cannot be critical);
- star-cap parity filter: since the seed side is tight, every proper
  3-edge-coloring of A gives the three cut edges pairwise distinct colors
  (skeptic-reviewed parity lemma, A17), and any color permutation is
  realizable; hence G is class 2 IFF R* = R + x + {x a_1, x a_2, x a_3} is
  class 2.  Only (R, attachment-triple) pairs with R* class 2 can produce a
  class-2 (hence critical) ambient, independently of the seed and matching.

For every Delta-critical ambient found: record cyclic-connectivity and
overfull status, then run the existential audit (all qualifying tight sides
of G, boundary-pair completions with short-circuit).  An ambient with NO
completing side refutes Lemma E (within the implemented conventions).

Guardrail: bounded finite search; failure to find an embedding does NOT prove
the seeds are unembeddable.  Do not send Songling-facing prose from this
audit without a fresh review/honesty gate.
"""
from __future__ import annotations

import argparse
import itertools
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

from critical_graph_search.edge_coloring import (  # noqa: E402
  _is_k_edge_colorable_from_endpoints,
  _prepare_endpoints,
  is_k_edge_colorable,
)
from critical_graph_search.density_filter import has_overfull_subgraph  # noqa: E402
import audit_songling_cyclic3_kempe_chain_request as kempe_audit  # noqa: E402
import lemma_e_stress_test_hereditary_failing_sides_20260610 as phase1  # noqa: E402

REPORTS_DIR = REPO_ROOT / ".hermes" / "reports"


def load_seeds(phase1_json: Path) -> list[dict[str, Any]]:
  payload = json.loads(phase1_json.read_text())
  seeds = [rec for rec in payload["failing_sides"] if rec.get("hereditarily_failing")]
  if not seeds:
    raise ValueError("no hereditarily failing seeds in the Phase 1 report")
  return seeds


def reverify_seed(graph6: str) -> tuple[nx.Graph, list[int]]:
  side = nx.from_graph6_bytes(graph6.encode())
  boundary = phase1.boundary_of(side)
  if len(boundary) != 3:
    raise ValueError(f"seed {graph6}: boundary is not 3 degree-2 vertices")
  if kempe_audit.has_cyclic_edge_cut_smaller_than_3(side):
    raise ValueError(f"seed {graph6}: has cyclic cut < 3")
  status = phase1.completion_status(side, boundary)
  if status["has_delta_critical_completion"]:
    raise ValueError(f"seed {graph6}: actually HAS a critical completion (phase 1 bug?)")
  analysis = phase1.analyze_failing_side(side, boundary)
  if not analysis["hereditarily_failing"]:
    raise ValueError(f"seed {graph6}: not hereditarily failing on re-check")
  return side, boundary


def build_r_pool(orders: list[int], geng_path: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
  pool: list[dict[str, Any]] = []
  stats = {
    "r_graphs": 0,
    "r_with_cycle": 0,
    "r_overfull_skipped": 0,
    "triples_tested": 0,
    "triples_class2_starcap": 0,
  }
  for n_r in orders:
    cmd = [geng_path, "-c", "-d1", "-D3", "-q", str(n_r)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    assert proc.stdout is not None
    for line in proc.stdout:
      g6 = line.strip()
      if not g6:
        continue
      stats["r_graphs"] += 1
      r = nx.from_graph6_bytes(g6.encode())
      if r.number_of_edges() < r.number_of_nodes():
        continue  # tree: no cycle, cut would not be cyclic
      stats["r_with_cycle"] += 1
      if has_overfull_subgraph(r, 3)[0]:
        # an overfull subset of R is an overfull subset of the ambient G,
        # and the theorem (hence Lemma E) only concerns non-overfull graphs
        stats["r_overfull_skipped"] += 1
        continue
      degree = dict(r.degree())
      deg1 = [v for v, d in degree.items() if d == 1]
      if len(deg1) > 3:
        continue
      eligible = [v for v, d in degree.items() if d <= 2]
      for triple in itertools.combinations(sorted(eligible), 3):
        if not set(deg1) <= set(triple):
          continue
        stats["triples_tested"] += 1
        star = r.copy()
        x = max(star.nodes()) + 1
        star.add_edges_from((x, a) for a in triple)
        if is_k_edge_colorable(star, 3):
          continue
        stats["triples_class2_starcap"] += 1
        pool.append({"graph6": g6, "n": r.number_of_nodes(), "attachments": list(triple)})
    proc.wait()
    if proc.returncode != 0:
      raise RuntimeError(f"geng exited {proc.returncode} for n_R={n_r}")
  return pool, stats


def ambient_is_overfull(g: nx.Graph) -> bool:
  """Fast overfull test for subcubic ambient candidates headed to criticality.

  In a subcubic graph, an odd set S is overfull iff deficiency(S) + out(S)
  <= 2, where deficiency(S) = sum over S of (3 - deg) and out(S) is the edge
  boundary.  The package's `has_overfull_subgraph` enumerates all 2^n odd
  subsets -- fine for the order-<=10 pool graphs, hopeless for 21-27-vertex
  ambients.  Here we only need correctness RELATIVE to the downstream
  criticality test, which rejects disconnected or bridged graphs anyway:
  - out(S) = 0 proper or def+out cases via single-edge cuts imply
    disconnection or a bridge (rejected later regardless), so
  - it suffices to test the whole graph arithmetically and, for proper S,
    every 2-edge-cut side (out(S) = 2, necessarily def(S) = 0 inside).
  """
  n = g.number_of_nodes()
  m = g.number_of_edges()
  if n % 2 == 1 and 2 * m > 3 * (n - 1):
    return True
  edges = list(g.edges())
  for i in range(len(edges)):
    for j in range(i + 1, len(edges)):
      h = g.copy()
      h.remove_edge(*edges[i])
      h.remove_edge(*edges[j])
      if nx.is_connected(h):
        continue
      for comp in nx.connected_components(h):
        if len(comp) % 2 == 0:
          continue
        out = sum(
          1 for e in (edges[i], edges[j]) if (e[0] in comp) != (e[1] in comp)
        )
        deficiency = sum(3 - g.degree(v) for v in comp)
        if deficiency + out <= 2:
          return True
  return False


def is_delta_critical_class2_known(g: nx.Graph) -> bool:
  """Criticality test for a graph already known class 2 via the parity filter.

  Mirrors `is_delta_critical` but runs the per-deletion colorability scan
  FIRST and the (guaranteed) class-2 exhaustion LAST as a sanity assert, so
  rejected gluings do not pay the full class-2 search-tree exhaustion.
  """
  if not nx.is_connected(g):
    return False
  if any(d < 2 for _, d in g.degree()):
    return False
  if any(nx.bridges(g)):
    return False
  edge_endpoints, n_vertices = _prepare_endpoints(g)
  for skip_idx in range(len(edge_endpoints)):
    if not _is_k_edge_colorable_from_endpoints(edge_endpoints, n_vertices, 3, skip_idx=skip_idx):
      return False
  if _is_k_edge_colorable_from_endpoints(edge_endpoints, n_vertices, 3):
    raise AssertionError(
      "glued graph is 3-edge-colorable despite the class-2 star-cap parity "
      "filter -- parity lemma or filter bug"
    )
  return True


def glue(seed: nx.Graph, boundary: list[int], r: nx.Graph, attachments: list[int], matching: tuple[int, ...]) -> nx.Graph:
  offset = max(seed.nodes()) + 1
  g = seed.copy()
  g.add_edges_from((u + offset, v + offset) for u, v in r.edges())
  for i, b in enumerate(boundary):
    g.add_edge(b, attachments[matching[i]] + offset)
  return g


def existential_audit(g: nx.Graph) -> dict[str, Any]:
  sides = kempe_audit.iter_qualifying_h_components(g, min_h_order=5)
  side_summaries: list[dict[str, Any]] = []
  any_completes = False
  for rec in sides:
    h = rec["h"]
    h_boundary = sorted(int(v) for v, d in h.degree() if d == 2)
    status = phase1.completion_status(h, h_boundary)
    side_summaries.append({
      "side_order": h.number_of_nodes(),
      "side_graph6": kempe_audit.graph6_string(h),
      "cut_edges": rec["cut_edges"],
      "has_delta_critical_completion": status["has_delta_critical_completion"],
    })
    if status["has_delta_critical_completion"]:
      any_completes = True
  return {
    "qualifying_sides": len(side_summaries),
    "some_side_completes": any_completes,
    "sides": side_summaries,
  }


def md_graph6(graph6: str) -> str:
  """Render graph6 safely in Markdown, including literal backticks."""
  escaped = (graph6.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace("`", "&#96;"))
  return f"<code>{escaped}</code>"


def main() -> int:
  parser = argparse.ArgumentParser(description="Lemma E Phase 2: ambient embedding hunt")
  parser.add_argument("--phase1-json", default=str(
    REPORTS_DIR / "lemma_e_stress_test_hereditary_failing_sides_20260610_081126.json"))
  parser.add_argument("--r-orders", nargs="+", type=int, default=[4, 5, 6, 7, 8, 9, 10])
  parser.add_argument("--geng-path", default="/usr/bin/geng")
  parser.add_argument("--max-ambients-per-seed", type=int, default=200)
  args = parser.parse_args()

  seed_records = load_seeds(Path(args.phase1_json))
  seeds: list[tuple[str, nx.Graph, list[int]]] = []
  for rec in seed_records:
    side, boundary = reverify_seed(rec["graph6"])
    seeds.append((rec["graph6"], side, boundary))
  print(f"re-verified {len(seeds)} hereditary seeds", flush=True)

  pool, pool_stats = build_r_pool(args.r_orders, args.geng_path)
  print(f"R pool: {pool_stats} -> {len(pool)} (R, attachment) candidates", flush=True)

  results: list[dict[str, Any]] = []
  lemma_e_refuted = False
  total_critical_ambients = 0
  total_glue_attempts = 0
  for seed_g6, seed, boundary in seeds:
    seed_result = {
      "seed_graph6": seed_g6,
      "glue_attempts": 0,
      "overfull_ambients_skipped": 0,
      "critical_ambients": 0,
      "ambients": [],
      "capped": False,
    }
    for cand in pool:
      r = nx.from_graph6_bytes(cand["graph6"].encode())
      for matching in itertools.permutations(range(3)):
        seed_result["glue_attempts"] += 1
        total_glue_attempts += 1
        g = glue(seed, boundary, r, cand["attachments"], matching)
        if ambient_is_overfull(g):
          seed_result["overfull_ambients_skipped"] += 1
          continue
        if not is_delta_critical_class2_known(g):
          continue
        total_critical_ambients += 1
        seed_result["critical_ambients"] += 1
        cyclic_lt3 = bool(kempe_audit.has_cyclic_edge_cut_smaller_than_3(g))
        overfull = False
        audit = existential_audit(g)
        ambient_record = {
          "ambient_graph6": kempe_audit.graph6_string(g),
          "ambient_order": g.number_of_nodes(),
          "r_graph6": cand["graph6"],
          "attachments": cand["attachments"],
          "matching": list(matching),
          "has_cyclic_cut_lt3": cyclic_lt3,
          "overfull": overfull,
          **audit,
        }
        seed_result["ambients"].append(ambient_record)
        flag = (not audit["some_side_completes"]) and not cyclic_lt3
        if flag:
          lemma_e_refuted = True
          print(f"*** LEMMA E REFUTED: ambient {ambient_record['ambient_graph6']} "
                f"(seed {seed_g6}): no qualifying side completes ***", flush=True)
        if seed_result["critical_ambients"] >= args.max_ambients_per_seed:
          seed_result["capped"] = True
          break
      if seed_result["capped"]:
        break
    print(f"seed {seed_g6}: {seed_result['glue_attempts']} gluings, "
          f"{seed_result['overfull_ambients_skipped']} overfull skipped, "
          f"{seed_result['critical_ambients']} critical non-overfull ambients"
          + (" (CAPPED)" if seed_result["capped"] else ""), flush=True)
    results.append(seed_result)

  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  rescued = sum(
    1 for r in results for a in r["ambients"] if a["some_side_completes"]
  )
  refuting = [
    a["ambient_graph6"]
    for r in results
    for a in r["ambients"]
    if not a["some_side_completes"] and not a["has_cyclic_cut_lt3"]
  ]
  report = {
    "generated_at": datetime.now().isoformat(timespec="seconds"),
    "question": (
      "Does any hereditary failing seed embed in a Delta-critical ambient "
      "graph with NO completing qualifying tight side (a Lemma E counterexample)?"
    ),
    "parameters": {
      "phase1_json": args.phase1_json,
      "r_orders": args.r_orders,
      "max_ambients_per_seed": args.max_ambients_per_seed,
    },
    "r_pool_stats": pool_stats,
    "summary": {
      "seeds": len(seeds),
      "total_glue_attempts": total_glue_attempts,
      "total_critical_ambients": total_critical_ambients,
      "ambients_with_completing_side": rescued,
      "refuting_ambients": refuting,
      "lemma_e_refuted_in_tested_scope": lemma_e_refuted,
      "scope_caveat": (
        "bounded gluing search (R orders as listed, single-seed ambients); "
        "absence of a refuting ambient here does not prove Lemma E"
      ),
    },
    "per_seed": results,
  }
  json_path = REPORTS_DIR / f"lemma_e_phase2_ambient_embedding_hunt_{timestamp}.json"
  json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

  lines = [
    "# Lemma E Phase 2: ambient embedding hunt",
    "",
    f"Generated: {report['generated_at']}",
    "",
    "## Summary",
    f"- Seeds (re-verified hereditary): {len(seeds)}",
    f"- R pool: {pool_stats['triples_class2_starcap']} class-2 star-cap (R, attachment) "
    f"candidates out of {pool_stats['triples_tested']} tested "
    f"(R orders {args.r_orders})",
    f"- Glue attempts: {total_glue_attempts}",
    f"- Delta-critical ambients found: {total_critical_ambients}",
    f"- Ambients where some side completes (rescued): {rescued}",
    f"- **Refuting ambients (non-overfull, no completing side, cyclically 3-edge-connected): {len(refuting)}**",
    f"- **Lemma E refuted in tested scope: {lemma_e_refuted}**",
    "",
    "## Per seed",
    "",
    "| seed | gluings | critical ambients | rescued | refuting | capped |",
    "|---|---:|---:|---:|---:|---|",
  ]
  for r in results:
    n_rescued = sum(1 for a in r["ambients"] if a["some_side_completes"])
    n_refuting = sum(1 for a in r["ambients"] if not a["some_side_completes"] and not a["has_cyclic_cut_lt3"])
    lines.append(
      f"| {md_graph6(r['seed_graph6'])} | {r['glue_attempts']} | {r['critical_ambients']} "
      f"| {n_rescued} | {n_refuting} | {r['capped']} |"
    )
  if refuting:
    lines.extend(["", "## Refuting ambients", ""])
    for g6 in refuting[:50]:
      lines.append(f"- {md_graph6(g6)}")
  lines.extend([
    "",
    "## Guardrails",
    "- Bounded finite search; no refuting ambient here does NOT prove Lemma E.",
    "- Guardrail: do not send Songling-facing prose from this audit without a fresh gate.",
    "",
    f"JSON sibling: `{json_path.name}`",
  ])
  md_path = REPORTS_DIR / f"lemma_e_phase2_ambient_embedding_hunt_{timestamp}.md"
  md_path.write_text("\n".join(lines) + "\n")
  print("\n".join(lines[:40]))
  print(f"\nwritten: {json_path}\nwritten: {md_path}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
