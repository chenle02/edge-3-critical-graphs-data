# Even snark-residue audit (orders < 22)

**Lemma.** For every snark S of order < 22, no graph obtained from S by deleting edges is a nontrivial 3-critical graph of even order.

**Verdict: LEMMA HOLDS** (0 counterexamples).

## Method
A snark is cubic (even order); edge deletion preserves the vertex set, so a residue S-F has the same even order as S. F=empty gives the cubic graph itself (regular, excluded by the census F2 filter); |F|=1 leaves exactly two degree-2 vertices (excluded by Jakobsen's theorem); the only residues keeping min-degree >= 2 delete a matching. Each residue is tested for: connected, Delta=3, no bridge, non-regular, class 2, edge-critical, and non-overfull.

## Direct edge-deletion residue audit (orders 10, 12, 14)

| Order | Cubic class-2 graphs | Residues tested | Even-order nontrivial 3-critical residues |
|---:|---:|---:|---:|
| 10 | 2 | 640 | 0 |
| 12 | 5 | 5,143 | 0 |
| 14 | 34 | 112,376 | 0 |

## Orders 18 and 20
See reports/songling_snark_critical_subgraph_audit.json: over all 1614 cubic class-2 graphs of order 18 and 14059 of order 20, every edge-3-critical subgraph is a vertex deletion (odd order); zero edge-deletion even-order 3-critical residues.

## Order 16 and all even orders
Covered by the exhaustive even-order census (results/order_N_delta_3.json): survivor_count = 0 at every even order 4..20. Snark edge-deletion residues are a subset of those graphs, hence 0.

Reproduce: `python3 code/scripts/audit_songling_even_snark_residue_below18.py` (needs `geng` from nauty).
