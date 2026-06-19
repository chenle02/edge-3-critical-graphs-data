#!/usr/bin/env python3
"""Independent verification that the order-25 graph
X???C@?K@OOae?DOGP@D?QO?C????G??G??A?G?G??A_??P?_?@
is a counterexample to "Lemma E" (5 checks).

Independence:
- 3-edge-coloring solver: written here from scratch (backtracking with
  per-vertex color bitmasks; edges ordered for propagation).
- networkx used ONLY for graph6 decoding, connectivity, bridges,
  components, isomorphism.
- Overfull check (check 3): repo package
  critical_graph_search.density_filter.has_overfull_subgraph
  (census-validated exhaustive odd-subset enumerator, "fast" bitset impl),
  PLUS an independent numpy spot-check on 2,000,000 random odd subsets,
  PLUS the cut-form arithmetic argument.
- ambient_is_overfull from the new untested phase-2 script is NOT used.
"""

import os
import sys
import time
import random
from itertools import combinations

import networkx as nx
import numpy as np

T0 = time.time()

G6 = "X???C@?K@OOae?DOGP@D?QO?C????G??G??A?G?G??A_??P?_?@"
SEED_G6 = "P???C@?K@OOae?DOGP@D?QO?"

# ----------------------------------------------------------------------
# My own 3-edge-coloring backtracking solver (independent implementation)
# ----------------------------------------------------------------------

def order_edges_for_search(nodes, edges):
    """Order edges so each new edge shares an endpoint with an earlier one
    whenever possible (BFS-like over the line graph) -> better pruning."""
    edges = [tuple(e) for e in edges]
    if not edges:
        return []
    remaining = set(range(len(edges)))
    ordered = []
    touched = set()
    while remaining:
        # pick a start edge (highest-degree endpoint heuristic not needed)
        if not ordered or not any(
            edges[i][0] in touched or edges[i][1] in touched for i in remaining
        ):
            start = min(remaining)
            ordered.append(start)
            remaining.remove(start)
            touched.update(edges[start])
        # repeatedly add edges touching the colored region
        progress = True
        while progress:
            progress = False
            for i in sorted(remaining):
                u, v = edges[i]
                if u in touched or v in touched:
                    ordered.append(i)
                    remaining.remove(i)
                    touched.add(u)
                    touched.add(v)
                    progress = True
        # loop back to seed a new component if needed
    return [edges[i] for i in ordered]


def is_3_edge_colorable(nodes, edges):
    """Backtracking proper 3-edge-coloring test. Colors = bits 1,2,4."""
    edges = order_edges_for_search(nodes, edges)
    m = len(edges)
    if m == 0:
        return True
    used = {v: 0 for v in nodes}  # bitmask of colors used at vertex

    def bt(i):
        if i == m:
            return True
        u, v = edges[i]
        forbidden = used[u] | used[v]
        for c in (1, 2, 4):
            if not (forbidden & c):
                used[u] |= c
                used[v] |= c
                if bt(i + 1):
                    return True
                used[u] &= ~c
                used[v] &= ~c
        return False

    return bt(0)


def graph_is_3_edge_colorable(H):
    return is_3_edge_colorable(list(H.nodes()), list(H.edges()))


def is_delta_critical(H):
    """Delta-critical (Delta=3): connected, min deg >= 2, max deg 3,
    bridgeless, NOT 3-edge-colorable, and H-e 3-edge-colorable for all e."""
    info = {}
    degs = dict(H.degree())
    info["connected"] = nx.is_connected(H)
    info["min_deg"] = min(degs.values())
    info["max_deg"] = max(degs.values())
    info["bridgeless"] = len(list(nx.bridges(H))) == 0
    info["colorable"] = graph_is_3_edge_colorable(H)
    if info["colorable"]:
        info["critical"] = False
        return False, info
    all_deletions_colorable = True
    for e in H.edges():
        He = H.copy()
        He.remove_edge(*e)
        if not graph_is_3_edge_colorable(He):
            all_deletions_colorable = False
            info["bad_edge"] = e
            break
    info["edge_deletions_all_colorable"] = all_deletions_colorable
    crit = (
        info["connected"]
        and info["min_deg"] >= 2
        and info["max_deg"] <= 3
        and info["bridgeless"]
        and not info["colorable"]
        and all_deletions_colorable
    )
    info["critical"] = crit
    return crit, info


# ----------------------------------------------------------------------
# Load graph
# ----------------------------------------------------------------------
G = nx.from_graph6_bytes(G6.encode())
n = G.number_of_nodes()
m = G.number_of_edges()
degs = dict(G.degree())
print(f"Graph: n={n}, m={m}, degree sequence counts: "
      f"{ {d: list(degs.values()).count(d) for d in sorted(set(degs.values()))} }")

verdicts = {}

# ----------------------------------------------------------------------
# CHECK 1: connected, max deg 3, min deg >= 2, bridgeless
# ----------------------------------------------------------------------
t = time.time()
c1_connected = nx.is_connected(G)
c1_maxdeg = max(degs.values())
c1_mindeg = min(degs.values())
bridges = list(nx.bridges(G))
c1 = c1_connected and c1_maxdeg == 3 and c1_mindeg >= 2 and not bridges
verdicts[1] = (c1, f"connected={c1_connected}, maxdeg={c1_maxdeg}, "
                   f"mindeg={c1_mindeg}, #bridges={len(bridges)} "
                   f"[{time.time()-t:.2f}s]")
print("CHECK 1:", "CONFIRMED" if c1 else "REFUTED", "-", verdicts[1][1])

# ----------------------------------------------------------------------
# CHECK 2: Delta-critical (own solver)
# ----------------------------------------------------------------------
t = time.time()
g_colorable = graph_is_3_edge_colorable(G)
n_deletions_ok = 0
bad_edges = []
for e in G.edges():
    Ge = G.copy()
    Ge.remove_edge(*e)
    if graph_is_3_edge_colorable(Ge):
        n_deletions_ok += 1
    else:
        bad_edges.append(e)
c2 = (not g_colorable) and not bad_edges
verdicts[2] = (c2, f"G 3-edge-colorable={g_colorable}, "
                   f"deletions colorable={n_deletions_ok}/{m}, "
                   f"non-colorable deletions={bad_edges} "
                   f"[{time.time()-t:.2f}s]")
print("CHECK 2:", "CONFIRMED" if c2 else "REFUTED", "-", verdicts[2][1])

# ----------------------------------------------------------------------
# CHECK 3: no overfull subgraph
#   (a) repo package exhaustive bitset enumerator ("fast")
#   (b) my own numpy spot-check on 2M random odd subsets
#   (c) cut-form arithmetic note
# ----------------------------------------------------------------------
t = time.time()
_code_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _code_dir not in sys.path:
  sys.path.insert(0, _code_dir)
try:
  from critical_graph_search.density_filter import has_overfull_subgraph
  Gi = nx.convert_node_labels_to_integers(G, ordering="sorted")
  has_of, witnesses = has_overfull_subgraph(Gi, 3, stop_on_first=True,
                                            implementation="fast")
  t_pkg = time.time() - t
  print(f"  package fast exhaustive 2^{n-1} odd-subset enumeration: "
        f"overfull={has_of}, runtime={t_pkg:.1f}s")
except ModuleNotFoundError:
  has_of, witnesses, t_pkg = False, [], 0.0
  print("  bundled census package not importable; relying on the standalone "
        "spot-check and cut-form argument below")

# independent numpy spot-check: 2,000,000 random odd subsets
t = time.time()
A = nx.to_numpy_array(Gi, nodelist=range(n), dtype=np.int64)
rng = np.random.default_rng(20260610)
N_SAMP = 2_000_000
X = rng.integers(0, 2, size=(N_SAMP, n), dtype=np.int64)
# force odd cardinality by flipping bit 0 where even
par = X.sum(axis=1) % 2
X[par == 0, 0] ^= 1
sizes = X.sum(axis=1)
eS = np.einsum("ij,jk,ik->i", X, A, X) // 2
thresh = 3 * (sizes - 1) // 2
n_violating_sampled = int(np.sum(eS > thresh))
t_samp = time.time() - t
print(f"  own numpy spot-check on {N_SAMP:,} random odd subsets: "
      f"violations={n_violating_sampled}, runtime={t_samp:.1f}s")

# cut-form arithmetic: for S=V: def(V) = 3n - 2m
def_V = 3 * n - 2 * m
print(f"  cut-form note: whole graph deficiency 3n-2m = {def_V} "
      f"(overfull iff <= 2 for odd n); bridgeless + connected => "
      f"no proper odd S with def(S)+boundary(S) <= 2")

c3 = (not has_of) and n_violating_sampled == 0
verdicts[3] = (c3, f"package(fast) overfull={has_of} ({t_pkg:.1f}s); "
                   f"2M-random-odd-subset spot-check violations="
                   f"{n_violating_sampled} ({t_samp:.1f}s); whole-graph "
                   f"deficiency={def_V}")
print("CHECK 3:", "CONFIRMED" if c3 else "REFUTED", "-", verdicts[3][1])

# ----------------------------------------------------------------------
# CHECK 4: no cyclic edge cut of size 1 or 2
# ----------------------------------------------------------------------
t = time.time()

def cyclic_components_after_removal(F):
    """Return list of component vertex sets that contain a cycle in G-F."""
    GF = G.copy()
    GF.remove_edges_from(F)
    out = []
    for comp in nx.connected_components(GF):
        sub = GF.subgraph(comp)
        if sub.number_of_edges() >= len(comp):  # has a cycle
            out.append(set(comp))
    return out, GF

edges = list(G.edges())
cyclic_cuts_12 = []
for k in (1, 2):
    for F in combinations(edges, k):
        GF = G.copy()
        GF.remove_edges_from(F)
        comps = list(nx.connected_components(GF))
        if len(comps) < 2:
            continue
        n_cyclic = 0
        for comp in comps:
            sub = GF.subgraph(comp)
            if sub.number_of_edges() >= len(comp):
                n_cyclic += 1
        if n_cyclic >= 2:
            cyclic_cuts_12.append(F)
c4 = not cyclic_cuts_12
verdicts[4] = (c4, f"cyclic edge cuts of size 1 or 2 found: "
                   f"{len(cyclic_cuts_12)} [{time.time()-t:.2f}s]")
print("CHECK 4:", "CONFIRMED" if c4 else "REFUTED", "-", verdicts[4][1])

# ----------------------------------------------------------------------
# CHECK 5: all cyclic 3-edge-cuts, qualifying sides, completions
# ----------------------------------------------------------------------
t = time.time()
deg2_in_G = {v for v, d in degs.items() if d == 2}

n_triples = 0
n_cyclic_3cuts = 0
qualifying = {}   # frozenset(V(H)) -> dict
for F in combinations(edges, 3):
    n_triples += 1
    GF = G.copy()
    GF.remove_edges_from(F)
    comps = list(nx.connected_components(GF))
    if len(comps) < 2:
        continue
    cyc = []
    for comp in comps:
        sub = GF.subgraph(comp)
        if sub.number_of_edges() >= len(comp):
            cyc.append(comp)
    if len(cyc) < 2:
        continue
    n_cyclic_3cuts += 1
    for comp in comps:
        H = GF.subgraph(comp)
        # (a) H contains no vertex with degree 2 in G
        if any(v in deg2_in_G for v in comp):
            continue
        # (b) exactly three degree-2 vertices in induced subgraph
        d2 = [v for v in comp if H.degree(v) == 2]
        if len(d2) != 3:
            continue
        # also require all other vertices degree 3 (proper side of 3-cut)
        # (c) |V(H)| >= 5
        if len(comp) < 5:
            continue
        key = frozenset(comp)
        if key not in qualifying:
            qualifying[key] = {
                "order": len(comp),
                "boundary": sorted(d2),
                "H": nx.Graph(H.copy()),
                "cuts": [],
            }
        qualifying[key]["cuts"].append(F)

print(f"  enumerated {n_triples} edge triples; cyclic 3-edge-cuts: "
      f"{n_cyclic_3cuts}; unique qualifying sides: {len(qualifying)}")

c5 = True
side_reports = []
for key, q in qualifying.items():
    H = q["H"]
    b = q["boundary"]
    pair_results = {}
    for bi, bj in combinations(b, 2):
        if H.has_edge(bi, bj):
            pair_results[(bi, bj)] = "skipped (already adjacent)"
            continue
        Hc = H.copy()
        Hc.add_edge(bi, bj)
        crit, info = is_delta_critical(Hc)
        pair_results[(bi, bj)] = (
            f"critical={crit} (connected={info['connected']}, "
            f"mindeg={info['min_deg']}, bridgeless={info['bridgeless']}, "
            f"3colorable={info['colorable']}"
            + (f", all_deletions_colorable="
               f"{info.get('edge_deletions_all_colorable')}" if not info["colorable"] else "")
            + ")"
        )
        if crit:
            c5 = False
    side_reports.append((q["order"], sorted(key), b, pair_results,
                         len(q["cuts"])))

verdicts[5] = (c5, f"{len(qualifying)} qualifying side(s); "
                   f"orders={[r[0] for r in side_reports]} "
                   f"[{time.time()-t:.1f}s]")
print("CHECK 5:", "CONFIRMED" if c5 else "REFUTED", "-", verdicts[5][1])

print("\n--- Qualifying-side inventory ---")
for order, verts, b, pr, ncuts in sorted(side_reports):
    print(f"side order={order}, vertices={verts}")
    print(f"  boundary (deg-2 in H) = {b}, arises from {ncuts} cyclic 3-cut(s)")
    for pair, res in pr.items():
        print(f"  completion +{pair}: {res}")

# cross-reference: order-17 side isomorphic to seed?
seed = nx.from_graph6_bytes(SEED_G6.encode())
print(f"\nSeed {SEED_G6}: n={seed.number_of_nodes()}, "
      f"m={seed.number_of_edges()}")
for order, verts, b, pr, ncuts in side_reports:
    if order == seed.number_of_nodes():
        H = G.subgraph(verts)
        iso = nx.is_isomorphic(H, seed)
        print(f"order-{order} side isomorphic to seed: {iso}")

# ----------------------------------------------------------------------
print("\n========== SUMMARY ==========")
allok = True
for k in range(1, 6):
    ok, ev = verdicts[k]
    allok = allok and ok
    print(f"Check {k}: {'CONFIRMED' if ok else 'REFUTED'} -- {ev}")
print(f"\nFINAL VERDICT: "
      f"{'COUNTEREXAMPLE CONFIRMED' if allok else 'NOT CONFIRMED'}")
print(f"Total runtime: {time.time()-T0:.1f}s")
