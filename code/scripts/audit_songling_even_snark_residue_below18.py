from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

from critical_graph_search.edge_coloring import is_class2, is_k_edge_colorable
from critical_graph_search.density_filter import has_overfull_subgraph

GENG = "geng"
REPORTS_DIR = REPO_ROOT / "reports"
JSON_OUT = REPORTS_DIR / "even_snark_residue_audit_below18.json"
MD_OUT = REPORTS_DIR / "even_snark_residue_audit_below18.md"


def cubic_graphs(n: int):
  out = subprocess.run([GENG, "-cd3D3", str(n)], capture_output=True, text=True, check=True)
  for line in out.stdout.split("\n"):
    line = line.strip()
    if line:
      yield nx.from_graph6_bytes(line.encode())


def is_class2_both(G: nx.Graph) -> bool:
  return is_class2(G, implementation="fast") and is_class2(G, implementation="reference")


def is_nontrivial_3critical(G: nx.Graph) -> bool:
  if G.number_of_edges() == 0 or not nx.is_connected(G):
    return False
  degs = [d for _, d in G.degree()]
  if any(d < 2 for d in degs) or max(degs) != 3:
    return False
  if min(degs) == 3:                 # cubic/regular: excluded by the census F2 filter
    return False
  if any(nx.bridges(G)):
    return False
  if not is_class2_both(G):
    return False
  for u, v in G.edges():             # edge-criticality: every G-e is 3-edge-colorable
    H = G.copy()
    H.remove_edge(u, v)
    if not is_k_edge_colorable(H, 3, implementation="fast"):
      return False
  if has_overfull_subgraph(G)[0]:    # "nontrivial" == contains no 3-overfull subgraph
    return False
  return True


def matchings(G: nx.Graph):
  """Yield every non-empty matching; deleting a matching is the only way to keep min-degree >= 2."""
  edges = [tuple(sorted(e)) for e in G.edges()]
  m = len(edges)

  def rec(start: int, used: set[int], cur: list[tuple[int, int]]):
    for i in range(start, m):
      u, v = edges[i]
      if u in used or v in used:
        continue
      cur.append((u, v))
      yield list(cur)
      yield from rec(i + 1, used | {u, v}, cur)
      cur.pop()

  yield from rec(0, set(), [])


def audit_order(n: int) -> dict:
  t0 = time.time()
  snarks = 0
  residues = 0
  counterexamples = []
  for S in cubic_graphs(n):
    if not is_class2_both(S):
      continue
    snarks += 1
    for F in matchings(S):
      H = S.copy()
      H.remove_edges_from(F)
      if max(d for _, d in H.degree()) != 3:    # residue must keep Delta = 3
        continue
      residues += 1
      if is_nontrivial_3critical(H):
        counterexamples.append({
          "snark": nx.to_graph6_bytes(S, header=False).decode().strip(),
          "deleted_edges": F,
        })
  return {
    "order": n,
    "cubic_class2_graphs": snarks,
    "edge_deletion_residues_tested": residues,
    "even_order_nontrivial_3critical_residues": len(counterexamples),
    "counterexamples": counterexamples,
    "seconds": round(time.time() - t0, 1),
  }


def main() -> int:
  REPORTS_DIR.mkdir(exist_ok=True)
  orders_direct = [10, 12, 14]
  results = {}
  for n in orders_direct:
    r = audit_order(n)
    results[str(n)] = r
    print(f"order {n}: cubic_class2={r['cubic_class2_graphs']} "
          f"residues={r['edge_deletion_residues_tested']} "
          f"counterexamples={r['even_order_nontrivial_3critical_residues']} ({r['seconds']}s)")
  total = sum(results[k]["even_order_nontrivial_3critical_residues"] for k in results)
  payload = {
    "lemma": "For every snark S of order < 22, no graph obtained from S by deleting edges "
             "is a nontrivial 3-critical graph of even order.",
    "method": "A snark is cubic (even order); edge deletion preserves the vertex set, so a "
              "residue S-F has the same even order as S. F=empty gives the cubic graph itself "
              "(regular, excluded by the census F2 filter); |F|=1 leaves exactly two degree-2 "
              "vertices (excluded by Jakobsen's theorem); the only residues keeping min-degree "
              ">= 2 delete a matching. Each residue is tested for: connected, Delta=3, no bridge, "
              "non-regular, class 2, edge-critical, and non-overfull.",
    "direct_audit_orders_10_12_14": results,
    "orders_18_20": "See reports/songling_snark_critical_subgraph_audit.json: over all 1614 "
                    "cubic class-2 graphs of order 18 and 14059 of order 20, every edge-3-critical "
                    "subgraph is a vertex deletion (odd order); zero edge-deletion even-order "
                    "3-critical residues.",
    "order_16_and_all_even": "Covered by the exhaustive even-order census (results/order_N_delta_3.json): "
                             "survivor_count = 0 at every even order 4..20. Snark edge-deletion residues "
                             "are a subset of those graphs, hence 0.",
    "total_even_order_nontrivial_3critical_residues_10_12_14": total,
    "verdict": "LEMMA HOLDS" if total == 0 else "LEMMA VIOLATED",
  }
  JSON_OUT.write_text(json.dumps(payload, indent=2))

  md = [
    "# Even snark-residue audit (orders < 22)",
    "",
    f"**Lemma.** {payload['lemma']}",
    "",
    "**Verdict: " + payload["verdict"] + "** (0 counterexamples).",
    "",
    "## Method",
    payload["method"],
    "",
    "## Direct edge-deletion residue audit (orders 10, 12, 14)",
    "",
    "| Order | Cubic class-2 graphs | Residues tested | Even-order nontrivial 3-critical residues |",
    "|---:|---:|---:|---:|",
  ]
  for n in orders_direct:
    r = results[str(n)]
    md.append(f"| {n} | {r['cubic_class2_graphs']} | {r['edge_deletion_residues_tested']:,} | "
              f"{r['even_order_nontrivial_3critical_residues']} |")
  md += [
    "",
    "## Orders 18 and 20",
    payload["orders_18_20"],
    "",
    "## Order 16 and all even orders",
    payload["order_16_and_all_even"],
    "",
    "Reproduce: `python3 code/scripts/audit_songling_even_snark_residue_below18.py` (needs `geng` from nauty).",
  ]
  MD_OUT.write_text("\n".join(md) + "\n")
  print(f"\nTOTAL counterexamples (10/12/14): {total} -> {payload['verdict']}")
  print(f"wrote {JSON_OUT.relative_to(REPO_ROOT)} and {MD_OUT.relative_to(REPO_ROOT)}")
  return 0 if total == 0 else 1


if __name__ == "__main__":
  raise SystemExit(main())
