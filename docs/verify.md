# Verify

The repository includes independent verification scripts and GitHub Actions checks. CI runs the verification on every push.

## Minimal local reproduction

```bash
git clone https://github.com/chenle02/edge-3-critical-graphs-data.git
cd edge-3-critical-graphs-data
pip install networkx numpy
python code/scripts/independent_verify_order25_witness.py
```

The script checks the order-25 witness logic used by the audit pipeline. The full repository also contains census outputs in `results/` and audit reports in `reports/` for independent inspection.

## Hash verification

The census-file SHA-256 values are stored only in the repository `README.md`. CI treats that table as canonical and checks the census files against it.
