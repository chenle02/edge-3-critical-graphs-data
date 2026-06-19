# Edge-chromatic 3-critical graphs — census data

This site documents the public research data repository for Le Chen and Songling Shan, *Exploring the world of edge-chromatic 3-critical graphs* (2026). The repository contains census outputs, verification code, and audit reports supporting the paper's computational classification statements.

A **nontrivial edge-chromatic 3-critical graph** here means a graph that is connected, has maximum degree 3, has chromatic index 4, becomes 3-edge-colorable after deleting any edge, and has no 3-overfull subgraph.

!!! note "Hash source of truth"
    The canonical SHA-256 values for census files live in the repository `README.md`. This site deliberately does **not** duplicate those hashes; CI checks the files against the README table.

## Census results

The table records the number of nontrivial survivors for each order in the public census range. Orders 20 and 23 are intentionally marked pending.

| Order | Nontrivial survivors | Status |
|---:|---:|---|
| 4 | 0 | determined |
| 5 | 0 | determined |
| 6 | 0 | determined |
| 7 | 0 | determined |
| 8 | 0 | determined |
| 9 | 0 | determined |
| 10 | 0 | determined |
| 11 | 0 | determined |
| 12 | 0 | determined |
| 13 | 14 | determined here |
| 14 | 0 | determined |
| 15 | 94 | determined here |
| 16 | 0 | determined |
| 17 | 774 | determined here |
| 18 | 0 | determined |
| 19 | 6,984 | determined here |
| 20 | pending | computation pending |
| 21 | 70,530 | determined here |
| 22 | 1 | Brinkmann--Steffen survivor reproduced |
| 23 | pending | computation pending |

Even orders below 22 have no nontrivial survivors. Odd orders 13 through 21 are determined by the census reported here. The order-22 survivor reproduces the Brinkmann--Steffen example.

## Repository contents

- `results/` — per-order survivor census files named `order_N_delta_3.json` or `order_N_delta_3.json.gz`.
- `reports/` — audit JSON files recording independent checks and pipeline summaries.
- `code/` — generation, filtering, verification, and audit scripts, including `code/scripts/independent_verify_order25_witness.py`.
- `README.md` — canonical census-file SHA-256 table and repository overview.

## Quick links

- [Methodology](methodology.md) — five-stage census pipeline.
- [Data dictionary](data.md) — JSON schema notes and loading snippet.
- [Results gallery](results.md) — per-order links and figure placeholders.
- [Interactive explorer](explorer.md) — standalone explorer entry point.
- [Verification](verify.md) — minimal reproduction instructions.
- [Cite](cite.md) — paper and dataset citation text.
