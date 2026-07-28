# Data and code for "Exploring the world of edge-chromatic 3-critical graphs"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub release](https://img.shields.io/github/v/release/chenle02/edge-3-critical-graphs-data)](https://github.com/chenle02/edge-3-critical-graphs-data/releases)
[![verify](https://github.com/chenle02/edge-3-critical-graphs-data/actions/workflows/verify.yml/badge.svg)](https://github.com/chenle02/edge-3-critical-graphs-data/actions/workflows/verify.yml)
[![website](https://img.shields.io/badge/website-online-blue)](https://chenle02.github.io/edge-3-critical-graphs-data/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20821990.svg)](https://doi.org/10.5281/zenodo.20821990)

![A sample of nontrivial edge-chromatic 3-critical graphs (orange = degree-2 vertices)](assets/hero.png)

**Website & interactive graph explorer:** <https://chenle02.github.io/edge-3-critical-graphs-data/>

This repository archives the census data, machine-readable audit reports, and
search/audit code referenced in the paper

> Le Chen and Songling Shan,
> *Exploring the world of edge-chromatic 3-critical graphs*, 2026.

A graph with maximum degree 3 is (edge-chromatic) **3-critical** if it is
connected, has chromatic index 4, and deleting any edge lowers the chromatic
index to 3.  A 3-critical graph is **nontrivial** if it contains no
3-overfull subgraph.  The paper determines the numbers of nontrivial
3-critical graphs for all orders through 24 — in particular the odd orders
15 through 23 — records complete computer censuses at orders 19, 21, and 23,
and independently reproduces the known order-22 and order-24 counts of
Brinkmann and Steffen.  Beyond
enumeration, the paper proves a **characterization theorem** for all
nontrivial 3-critical graphs in terms of four construction mechanisms
(vertex-blowup, Haj\u00f3s-join, Meredith-type extension, and
snark-completion), and this
repository's classification script gives a deterministic five-label software
partition of every survivor. Because its Meredith test uses only smaller
cyclic-cut shores, that partition is census bookkeeping rather than an exact
disjoint partition by theorem clauses.

The completed **Order-23 census** has 782,186 nontrivial survivors.  The
completed **Order-24 census** has exactly nine; eight are
contractible-triangle blowups of the unique order-22 survivor, while the
triangle-free fifth graph is primitive under this operation.

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
results/   complete census output files, orders 4 through 24
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
| `order_20_delta_3.json.gz` | 0 | `08e25a09ecdedd06b8904342203307ad71728aa609f5469d160ac9ce32ac8ed0` |
| `order_21_delta_3.json.gz` | 70,530 | `2f9c3e46d744dc0b62a95631e050af657806ec76ae03a286f7e845c69cff24db` |
| `order_22_delta_3.json.gz` | 1 | `57dbfccd9cb352564f5422530c9a0b7e269148c9789bf040f0dfd7ab96ed553e` |
| `order_23_delta_3.json.gz` | 782,186 | `d5c9cf97ab8c2b693a24ecd4970e328a51210b302774b5506a200f7371a28896` |
| `order_24_delta_3.json.gz` | 9 | `81dc57cef8680b4908e7159b186543209ce276b8fb3d6dff57e744ee68725523` |

The hashes for `order_20`, `order_21`, and `order_22` are of the compressed files, as
archived here and as recorded during the original runs.

## Computational effort

Exact Easley Slurm accounting is archived for the completed Order-21 and
Order-22 censuses. Order 21 used **8,964.720 core-hours** to process
1,068,435,908 graphs; Order 22 used **1,983.053 core-hours** to process
5,022,269,988 graphs. Both campaigns consisted of 16 successful 48-CPU tasks
with no retries recorded. Their calendar spans were 23:52:47 and 5:20:59,
respectively.

### Order-23 extension (complete)

The 64-slice Order-23 census completed on **2026-07-23**. The campaign ran from
**2026-05-29T22:16:47** to **2026-07-23T09:54:02** (America/Chicago), a calendar
span of 54d 11:37:15, with all **64/64 slices** reaching a final result. Its
final counters are 24,086,917,749 processed, 39,229,986 pruned, critical
240,892,267, overfull 240,110,081, and **782,186 nontrivial survivors** (the
merged census file `order_23_delta_3.json.gz` above). The 106 Slurm attempts
represent a cumulative **939d 08:50:09** of wall time and **723,371.786
core-hours** of allocated compute.

See the [computational-effort overview](docs/computational-effort.md), including
links to the detailed per-slice reports and machine-readable telemetry. For
Order 23, see the canonical [JSON snapshot](reports/order23_computational_effort_20260723.json)
and the [TSV telemetry](reports/order23_computational_effort_20260723.tsv).

### Order-24 extension (complete)

The 1024-slice Order-24 census completed with no failed final slices and found
exactly **9** nontrivial survivors. All nine were independently rechecked for
edge-criticality and non-overfullness. The native streaming filter retained
only survivor records, so the archived merged JSON deliberately does not claim
an exact raw candidate count; the pre-flight population estimate was about
3.4×10¹¹ graphs. The campaign used approximately 1,230 allocated core-hours
over a 13.3-hour wall-clock span on Auburn's Easley cluster.

This work was completed in part with resources provided by the Auburn University Easley Cluster.

## Audit reports (`reports/`)

Reports are archived as produced by the audit runs (provenance copies, with
local absolute paths and internal review notes redacted; JSON is the canonical
record, Markdown siblings are human-readable summaries).  The reports
supporting the paper:

| Paper reference | File(s) |
|---|---|
| Census categorization by characterization clauses (Table in the paper) | `census_characterization_classification.json`, `census_characterization_classification.md` |
| Order-13 construction classification | `order13_triangle_blowup_classification.json`, `delta3_blowup_chain_9_11_13.json` |
| Order-15/17 construction passes | `songling_order15_order17_generation_verification.json`, `..._second_pass.json`, `..._third_pass_hajos.json` |
| Residual records | `songling_remaining_residue_dossier.json` |
| Even-order snark-residue audit (orders < 18) | `even_snark_residue_audit_below18.json` |
| Snark-deletion comparisons | `songling_snark_critical_subgraph_audit.json`, `songling_order17_snark_candidate_audit.json`, `songling_sve_hajos_followup_audit_20260505.*` |
| Cyclic 3-cut side characterization ledger | `songling_h_characterization_ledger_20260602_ledger.json` |

## Code (`code/`)

- `code/critical_graph_search/` and `code/main.py`: the census pipeline
  (graph generation via `geng` from the nauty suite, pruning filters,
  bitmask backtracking edge-coloring, criticality and overfull tests).
- `code/scripts/classify_census_characterization.py`: the deterministic
  census post-processor that assigns every nontrivial survivor the first
  applicable software label: (a) vertex-blowup, (b) Haj\u00f3s-join, (c)
  smaller-shore Meredith-type, or residual (d)/(e). It asserts that these
  five labels partition each order exactly. The Meredith test deliberately
  checks only smaller cyclic-cut shores, so residual labels do not certify
  failure of theorem clause (c). It reproduces the software table:
  ```bash
  python3 code/scripts/classify_census_characterization.py --orders 13 15 17 19 21 22 23
  ```
- `code/scripts/audit_songling_snark_critical_subgraphs.py`,
  `code/scripts/audit_songling_even_snark_residue_below18.py`,
  `code/scripts/audit_songling_cyclic3_kempe_chain_request.py`: snark- and
  cyclic-3-cut audits supporting the snark-completion clauses.
- `code/scripts/analyze_pattern_i_boundary_states.py` and
  `code/scripts/analyze_pattern_ii_boundary_states.py`: exact finite
  boundary-state certificates used in the all-order snark-completion proof.
  Their tests verify the complete family counts and parity conclusions:
  ```bash
  python3 -m pytest \
    code/tests/test_analyze_pattern_i_boundary_states.py \
    code/tests/test_analyze_pattern_ii_boundary_states.py
  ```
- `code/scripts/classify_order24_survivors.py`: independently reproduces the
  split of the nine order-24 survivors into eight triangle blowups of the
  order-22 survivor and one triangle-free primitive graph:
  ```bash
  python3 code/scripts/classify_order24_survivors.py
  ```
- `code/scripts/check_hashes.py`: recompute and verify the census SHA-256
  hashes recorded above.
- `code/scripts/export_explorer_data.py`, `code/scripts/render_graphs.py`:
  data export for the website explorer and figure rendering.

The audit scripts are archived as run; some refer to paths in the private
research repository where they were executed. The census pipeline, the
classification script, and the hash check run against this repository alone.

## Reproducibility and environment

Tested toolchain:

- **Python** 3.10-3.12 (continuous integration runs on 3.11).
- **Python packages** (see [`code/requirements.txt`](code/requirements.txt)):
  `networkx>=3.0`, `numpy>=1.24`; `matplotlib>=3.7` (figures) and
  `pytest>=7.0` (tests) are optional.
- **External tool:** graph generation calls **`geng` from nauty 2.8.9**
  (install via `apt install nauty`, `brew install nauty`, or from
  <https://pallini.di.uniroma1.it/>). The verifier and hash checks do not
  need nauty.

Set up and verify the paper's census claims:

```bash
python3 -m pip install -r code/requirements.txt
# Confirm the archived census files match the recorded SHA-256 hashes:
python3 code/scripts/check_hashes.py --readme README.md --results-dir results
```

Census generation at order `n` uses the exact invocation
`geng -Cq -d2 -D3 n` (2-connected, minimum degree >= 2, maximum degree <= 3);
the driver is `code/main.py`. The per-order JSON files under `results/` are the
manuscript-facing records, and their SHA-256 hashes (above) are the source of
truth tying each file to the counts reported in the paper.

## Use of AI tools

In the spirit of the [SIAM Editorial Policy on Artificial
Intelligence](https://epubs.siam.org/artificial-intelligence) and for full
transparency, we record that AI-based tools (large language models and AI
coding assistants) were used to help develop, debug, and document the search
and audit code in this repository, and to assist with drafting the manuscript.
The candidate graphs were generated by `geng` from the nauty suite, and the
census, criticality, and overfull results were produced by the code archived
here. The authors reviewed, tested, and verified all AI-assisted code; the
SHA-256 hash check above lets any reader confirm the census files behind the
paper's counts directly from this repository. The authors assume responsibility
for all content.

## The order-25 witness

The impossibility theorem's witness is the order-25 graph with graph6 string

```
X???C@?K@OOae?DOGP@D?QO?C????G??G??A?G?G??A_??P?_?@
```

Run `python3 code/scripts/independent_verify_order25_witness.py` to check
all of its claimed properties end to end.

## Acknowledgment

This work was completed in part with resources provided by the Auburn University Easley Cluster.

## License

MIT (see LICENSE).
