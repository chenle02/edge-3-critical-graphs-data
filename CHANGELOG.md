# Changelog

All notable changes to this repository are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [v1.1.1] - 2026-06-24

Housekeeping release: redacted local absolute paths and an internal review note
from the archived `reports/` provenance copies, and made
`classify_census_characterization.py` record repository-relative input paths.
No census data or counts changed; all SHA-256 hashes remain identical to v1.0.0.
Concept DOI [10.5281/zenodo.20821990](https://doi.org/10.5281/zenodo.20821990)
(always resolves to this latest version).

## [v1.1.0] - 2026-06-24

Archived on Zenodo: concept DOI [10.5281/zenodo.20821990](https://doi.org/10.5281/zenodo.20821990)
(always latest); version DOI [10.5281/zenodo.20821991](https://doi.org/10.5281/zenodo.20821991).

Reproducibility and submission-readiness hardening accompanying the submission
of the paper to the *SIAM Journal on Discrete Mathematics*, in compliance with
the SIAM Editorial Policy on Artificial Intelligence (v2.0).

**No census data changed.** Every file under `results/` and `reports/` is
byte-for-byte identical to v1.0.0, so all SHA-256 hashes recorded in
`README.md` and in the manuscript remain valid.

### Added
- `CHANGELOG.md` (this file).
- `code/scripts/classify_census_characterization.py`: the deterministic
  classification script cited by the paper, which partitions every survivor by
  the characterization theorem's clauses (a)-(e). It reproduces the paper's
  categorization table exactly (e.g. order 19: 5928/6984 vertex-blowup; order
  21: 60479/70530), and its output is archived in
  `reports/census_characterization_classification.{json,md}`.
- "Reproducibility and environment" section in `README.md` documenting the
  tested toolchain (Python 3.10-3.12, nauty 2.8.9) and the exact `geng`
  invocation used for graph generation.
- "Use of AI tools" provenance section in `README.md`, mirroring the
  manuscript's *Declaration of Use of AI Tools*: the authors reviewed and
  verified all AI-assisted code and assume responsibility for all content.
- `numpy` listed explicitly in `code/requirements.txt`.
- `license`, author affiliations, keywords, project URL, and release date
  fields in `CITATION.cff`.

### Changed
- Scoped the repository to match the submitted paper. `README.md`, `docs/`,
  and the verification workflow now describe exactly the census (orders 4-22)
  and the characterization theorem.
- `code/requirements.txt` now records tested version floors and documents the
  external nauty/`geng` dependency and how to install it.
- CI (`verify.yml`) now checks the census hashes and reproduces the
  categorization, instead of the removed witness check.
- `CITATION.cff` version bumped to `v1.1.0`.

### Removed
- Exploratory "Lemma E" / boundary-completion material that was **not part of
  the submitted paper**: `code/scripts/independent_verify_order25_witness.py`,
  `code/scripts/lemma_e_*`, `code/scripts/audit_lemma24_boundary_completion_repair.py`,
  and the corresponding `reports/lemma_e_*` and
  `reports/lemma24_boundary_completion_*` files. This material remains
  available in the project's git history and private research repository for
  future development.

### Preserved
- All census outputs (`results/`, orders 4-22) verified unchanged via
  `code/scripts/check_hashes.py` (every SHA-256 hash identical to v1.0.0).

## [v1.0.0] - 2026

Initial public release: census data (orders 4-22), machine-readable audit
reports, the search/audit code (`critical_graph_search` package, pipeline
driver, and audit scripts), the MkDocs-Material website with the interactive
graph explorer, continuous-integration verification, and citation metadata.
