# Data dictionary

The census files in `results/` are JSON or gzipped JSON files. The canonical SHA-256 hashes for those files live in the repository `README.md`, and CI checks the census files against that table.

## Survivor JSON schema

Each per-order file records metadata for one census order and a list of survivor graphs. The exact audit metadata may vary by file, but survivor entries are intended to be self-contained enough to rebuild the graph.

Typical top-level fields:

| Field | Meaning |
|---|---|
| `order` | Number of vertices `n`. |
| `delta` | Maximum degree, equal to 3 for this census. |
| `survivor_count` | Number of nontrivial survivors in the file. |
| `survivors` | Array of survivor graph records. |
| `metadata` | Optional generation, software, or audit metadata. |

Typical survivor-record fields:

| Field | Meaning |
|---|---|
| `id` | Stable record identifier within the census file. |
| `n` or `order` | Number of vertices. |
| `edges` | Edge list using integer vertex labels; this is the easiest field for rebuilding the graph. |
| `graph6` | Optional compact graph6 encoding of the same unlabeled graph. |
| `invariants` | Optional precomputed graph invariants used for audit or browsing. |

## graph6 encoding

`graph6` is a compact ASCII format for simple undirected graphs, widely used by nauty and NetworkX. It is convenient for deduplicating, comparing, and transferring graphs. When both `edges` and `graph6` are present, the edge list is the most direct reconstruction path for scripts, while `graph6` is useful for interoperability with graph-census tools.

## Loading a survivor with Python

```python
import json, networkx as nx
data = json.load(open("results/order_13_delta_3.json"))
record = data["survivors"][0]
G = nx.Graph(record["edges"])
```

For `.json.gz` files, open the file with Python's `gzip.open(..., "rt")` before passing it to `json.load`.

## Hashes and CI

Do not copy SHA-256 values from the README into downstream documents. The README's census-file table is the single source of truth, and continuous integration checks those hashes on every push.
