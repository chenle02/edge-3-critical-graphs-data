# H-characterization ledger for Songling manuscript patch

Generated: 2026-06-02T19:34:20

## Scope and caution
- Complete class ledger: All tested tied minimal H components in the complete original/aut-orbit Kotzig boundary-cache artifact. Isomorphism preserves the boundary set {0,1,2} but not the individual names of 0,1,2.
- Modified/fixed12 aggregation: Graph-level category counts come from the compact modified-Kotzig and fixed-(1,2)-Kempe-chain audit artifacts. Those compact artifacts record aggregate unique-H counts and samples, not every per-H class assignment; the manuscript wording therefore uses aggregate counts and treats the class ledger as audit provenance, not as a theorem-level classification by final category.

## Graph-record partition for the manuscript
- Modified Kotzig x/triangle-blowup pass: 18554 graph records.
- Modified-Kotzig fail but fixed-(1,2)-Kempe-chain pass: 1025 graph records.
- Remaining after both tests: 179 graph records.

By order:
- order 13: modified=3, fixed12=0, remaining=0
- order 15: modified=26, fixed12=0, remaining=0
- order 17: modified=209, fixed12=0, remaining=0
- order 19: modified=1726, fixed12=27, remaining=5
- order 21: modified=16590, fixed12=998, remaining=174

## Unique-H ledger anchors
- Complete original/aut-orbit artifact: 4053 boundary-first H graph6 keys, merging to 2922 boundary-set isomorphism classes.
- Modified-Kotzig audit evaluated 4066 unique minimal H graphs.
- Fixed-(1,2) audit tested 742 unique H graphs among modified failures: 626 passing and 116 failing.

## Representatives for figure
- kotzig_formation_pass: class H0001, graph6 `D]o`, |V(H)|=5, |E(H)|=6 (complete original/aut-orbit Kotzig audit artifact).
- fixed12_pass_after_modified_fail: class H2923, graph6 `JE@_@OYBcE?`, |V(H)|=11, |E(H)|=15 (fixed-(1,2)-chain audit passing_h_sample).
- remaining_after_fixed12: class H2924, graph6 `JEH??oe@sS?`, |V(H)|=11, |E(H)|=15 (fixed-(1,2)-chain audit failing_h_sample).

## Outputs
- JSON: `.hermes/reports/songling_h_characterization_ledger_20260602_ledger.json`
- CSV: `.hermes/reports/songling_h_characterization_class_ledger_20260602_ledger.csv`
- PNG: `notes/assets/songling-h-characterization-representatives-20260602.png`
- PDF: `notes/assets/songling-h-characterization-representatives-20260602.pdf`

## Source hashes
```json
{
  ".hermes/reports/songling_failed_h_fixed12_chain_property_rerun_20260602_0735.json": "a8d7c4483954513b7f8b27e559201eb8e719e85b51de97011eaa8eab6eb23d58",
  ".hermes/reports/songling_kotzig_formation_counts_from_boundary_cache_20260601_214847.json": "8f8b5b5ba9a45960126c5b9b0848378617cd5f62553178e787aca19648a2bfec",
  ".hermes/reports/songling_modified_kotzig_formation_audit_20260602.json": "313394eaa661f4772ef1885fc0297c0e2c0f8b64f92e26c16cd4dacb7a49656a"
}
```

## Output hashes
```json
{
  ".hermes/reports/songling_h_characterization_class_ledger_20260602_ledger.csv": "f9ed416a1d0ad1931b5b8b46a49889d8930da37e7617457b16d200884ee8428c",
  ".hermes/reports/songling_h_characterization_ledger_20260602_ledger.json": "64b1f729b7ce073b8184e7f9ac43809ad0928c592b085887c3c70118d461668a",
  ".hermes/reports/songling_h_characterization_ledger_20260602_ledger.md": "3c2323ac39baea27064f7d9b9b95b4ed72dd60a49397b075f040da4ec93dc166",
  "notes/assets/songling-h-characterization-representatives-20260602.pdf": "40470e53a34edacaa016e27a15aefb0c48be9c44f0bac66a2a2a574aed90402a",
  "notes/assets/songling-h-characterization-representatives-20260602.png": "d1e9f1d1ccc70a44e5f41729e7ef4cac6a6eb5c203bb37fbe358c5d691ea3fa6"
}
```
## Local send gate
- No Overleaf edit, email, Telegram message, staging, commit, or push is authorized by this ledger hardening.
