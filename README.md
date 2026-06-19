# Data and code for "Exploring the world of edge-chromatic 3-critical graphs"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/chenle02/edge-3-critical-graphs-data)](https://github.com/chenle02/edge-3-critical-graphs-data/releases)
[![verify](https://github.com/chenle02/edge-3-critical-graphs-data/actions/workflows/verify.yml/badge.svg)](https://github.com/chenle02/edge-3-critical-graphs-data/actions/workflows/verify.yml)
[![website](https://img.shields.io/badge/website-online-blue)](https://chenle02.github.io/edge-3-critical-graphs-data/)
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.TODO.svg)](https://doi.org/10.5281/zenodo.TODO) -->

![A sample of nontrivial edge-chromatic 3-critical graphs (orange = degree-2 vertices)](assets/hero.png)

**Website & interactive graph explorer:** <https://chenle02.github.io/edge-3-critical-graphs-data/>

This repository archives the census data, machine-readable audit reports, and
search/audit code referenced in the paper

> Le Chen and Songling Shan,
> *Exploring the world of edge-chromatic 3-critical graphs*, 2026.

A graph with maximum degree 3 is (edge-chromatic) **3-critical** if it is
connected, has chromatic index 4, and deleting any edge lowers the chromatic
index to 3.  A 3-critical graph is **nontrivial** if it contains no
3-overfull subgraph.  The paper determines the exact numbers of nontrivial
3-critical graphs of orders 13, 15, and 17, records complete computer
censuses at orders 19 and 21, reproduces the known order-22 count, gives a
finite construction ledger for the audited census, and proves two structural
results delimiting the cyclic 3-edge-cut method (an all-order one-sided
triangle-cap reduction, and an impossibility theorem for the
boundary-completion reconstruction, with explicit witnesses of orders 25
and 27).

## Quickstart

```python
import json, gzip, networkx as nx

# load a census file (.json, or gzip.open(..., "rt") for .json.gz)
data = json.load(open("results/order_13_delta_3.json"))
print(data["survivor_count"], "nontrivial survivors at order", data["order"])

# rebuild any survivor as a networkx graph from its edge list
G = nx.Graph(); G.add_edges_from(data["survivors"][0]["edges"])
print("example survivor:", G)
```

Browse every order interactively (live graph rendering) on the
[website](https://chenle02.github.io/edge-3-critical-graphs-data/).

## Layout

```
results/   complete census output files, orders 4 through 22
reports/   machine-readable audit reports cited in the paper
code/      search pipeline and audit scripts
```

## Census files (`results/`)

Each `order_n_delta_3.json` (or `.json.gz`) records the full census run at
order `n`: number of generated 2-connected subcubic graphs, number of
3-critical graphs, number of overfull ones, and the list of nontrivial
survivors in graph6 format.  SHA-256 hashes of the files backing the paper's
headline counts:

| File | Survivors | SHA-256 |
|---|---:|---|
| `order_13_delta_3.json` | 14 | `799aae0712bfb53b10279cdb178abd9ae2b55924f134d2fd3f9154ad4527ef10` |
| `order_15_delta_3.json` | 94 | `c5c391d32a4019a6765e236ac9bfbd292572722073fbb72312d4ecbf91293162` |
| `order_17_delta_3.json` | 774 | `c7447e9626f53cdb8a381376ec76eb95a58368bab85dd16dd02ba6d4f7b9a269` |
| `order_19_delta_3.json` | 6,984 | `9f4eff7e13636fce3bcd3fc69cd2a3dfb36f1ad80e01656509fc6b9927f92b1e` |
| `order_21_delta_3.json.gz` | 70,530 | `2f9c3e46d744dc0b62a95631e050af657806ec76ae03a286f7e845c69cff24db` |
| `order_22_delta_3.json.gz` | 1 | `57dbfccd9cb352564f5422530c9a0b7e269148c9789bf040f0dfd7ab96ed553e` |

The hashes for `order_21` and `order_22` are of the compressed files, as
archived here and as recorded during the original runs.

## Audit reports (`reports/`)

Reports are archived exactly as produced by the audit runs (provenance
copies; JSON is the canonical record, Markdown siblings are human-readable
summaries).  The reports cited in the paper:

| Paper reference | File(s) |
|---|---|
| Finite boundary-completion audit, orders 13-19 | `lemma24_boundary_completion_census_audit_20260601_190638.json.gz` |
| Finite boundary-completion audit, order 21 | `lemma24_boundary_completion_census_audit_20260601_212852.json.gz` |
| Exhaustive tight-side enumeration, orders 7-13 | `lemma_e_stress_test_hereditary_failing_sides_20260610_045602.json` |
| Exhaustive tight-side enumeration, orders 15-17 | `lemma_e_stress_test_hereditary_failing_sides_20260610_081126.json` |
| Gluing search and witness list (92 witnesses, orders 25/27) | `lemma_e_phase2_ambient_embedding_hunt_20260610_120153.json` |
| Order-13 construction classification | `order13_triangle_blowup_classification.json`, `delta3_blowup_chain_9_11_13.json` |
| Order-15/17 construction passes | `songling_order15_order17_generation_verification.json`, `..._second_pass.json`, `..._third_pass_hajos.json` |
| Residual records | `songling_remaining_residue_dossier.json` |
| Snark-deletion comparisons | `songling_snark_critical_subgraph_audit.json`, `songling_order17_snark_candidate_audit.json`, `songling_sve_hajos_followup_audit_20260505.*` |
| Cyclic 3-cut side characterization ledger | `songling_h_characterization_ledger_20260602_ledger.json` |

Note on terminology: some artifacts use the internal working name
"Lemma E" for the all-order boundary-completion property; that property is
exactly the one refuted by the impossibility theorem of the paper.

## Code (`code/`)

- `code/critical_graph_search/` and `code/main.py`: the census pipeline
  (graph generation via `geng` from the nauty suite, pruning filters,
  bitmask backtracking edge-coloring, criticality and overfull tests).
- `code/scripts/audit_lemma24_boundary_completion_repair.py`: the
  boundary-completion audit behind the finite audit proposition.
- `code/scripts/audit_songling_cyclic3_kempe_chain_request.py`: shared
  cyclic 3-cut side-enumeration helpers.
- `code/scripts/lemma_e_stress_test_hereditary_failing_sides_20260610.py`:
  exhaustive tight-side-shape enumeration (orders 7-17).
- `code/scripts/lemma_e_phase2_ambient_embedding_hunt_20260610.py`:
  the bounded gluing search producing the 92 witnesses.
- `code/scripts/independent_verify_order25_witness.py`: a standalone,
  from-scratch verifier (own backtracking solver, exhaustive odd-subset
  overfull check, exhaustive small-cut scans) for the order-25 witness of
  the impossibility theorem.  It depends only on `networkx` and `numpy`.

The audit scripts are archived as run; some refer to paths in the private
research repository where they were executed.  The independent verifier is
standalone and reproduces, in under a minute, every property of the
order-25 witness claimed in the paper.

Requirements: Python 3.10+, `networkx` (and `numpy` for the independent
verifier); graph generation additionally requires `geng` from the nauty
suite.

## The order-25 witness

The impossibility theorem's witness is the order-25 graph with graph6 string

```
X???C@?K@OOae?DOGP@D?QO?C????G??G??A?G?G??A_??P?_?@
```

Run `python3 code/scripts/independent_verify_order25_witness.py` to check
all of its claimed properties end to end.

## License

MIT (see LICENSE).
