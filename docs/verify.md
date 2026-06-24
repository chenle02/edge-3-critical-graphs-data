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
python code/scripts/classify_census_characterization.py --orders 13 15 17 19 21 22
```

The classification script asserts that the clauses (a)-(e) of the
characterization theorem partition each order's survivor set exactly, and
reproduces the categorization table in the paper. The full repository also
contains census outputs in `results/` and audit reports in `reports/` for
independent inspection.

## Hash verification

The census-file SHA-256 values are stored only in the repository `README.md`. CI treats that table as canonical and checks the census files against it.
