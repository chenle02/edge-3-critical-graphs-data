# Verify

The repository includes independent verification scripts and GitHub Actions checks. CI runs the verification on every push.

## Minimal local reproduction

```bash
git clone https://github.com/chenle02/edge-3-critical-graphs-data.git
cd edge-3-critical-graphs-data
pip install -r code/requirements.txt
# verify the census files against the recorded SHA-256 hashes:
python code/scripts/check_hashes.py --readme README.md --results-dir results
# reproduce the paper's census categorization by characterization clauses:
python code/scripts/classify_census_characterization.py --orders 13 15 17 19 21 22 23
# verify the finite Pattern-I and Pattern-II proof certificates:
python -m pytest \
  code/tests/test_analyze_pattern_i_boundary_states.py \
  code/tests/test_analyze_pattern_ii_boundary_states.py
```

The classification script asserts that its five deterministic software labels
partition each order's survivor set exactly. Its Meredith test examines only
subset-minimal smaller cyclic-3-cut shores, whereas theorem clause (c) permits
either shore. Consequently, a residual `(d/e)` label need not exclude clause
(c); the output is census bookkeeping, not a computational proof of an exact
disjoint theorem-clause partition. The full repository also contains census
outputs in `results/` and audit reports in `reports/` for independent
inspection.

## Boundary-state proof certificates

The Pattern-I certificate enumerates all nonempty families of the five
equality types on a three-port boundary and finds exactly the six ordered
family pairs stated in the manuscript. The Pattern-II certificate enumerates
the five equality types on three ports, the fourteen equality types on four
ports, and a necessary Kempe-component-partition closure. It verifies the
reported 23 and 3,767 admissible families, 81 critical connector triples, and
the parity conclusion that every non-singleton corner contains at least two
degree-2 vertices.

The Pattern-II closure is deliberately a relaxation: passing it does not
assert that a family is realizable by a graph. This is the rigorous direction
needed in the proof, because every realizable corner family must pass the
relaxation and hence occurs in the enumerated list.

## Hash verification

The census-file SHA-256 values are stored only in the repository `README.md`. CI treats that table as canonical and checks the census files against it.
