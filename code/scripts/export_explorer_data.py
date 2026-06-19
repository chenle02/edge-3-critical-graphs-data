#!/usr/bin/env python3
"""Export compact explorer data for the edge-3-critical graph census.

Reads read-only census files from /tmp/opencode/e3c/shared/data and writes
relative JSON assets under ./assets/data for the standalone explorer.
Only the Python standard library is used.
"""

from __future__ import annotations

import gzip
import json
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = Path("/tmp/opencode/e3c/shared/data")
OUT = ROOT / "assets" / "data"
ORDERS = (9, 11, 13, 15, 17, 19, 21, 22)
SAMPLE_SIZE = 200
FULL_EXPORT_ORDERS = {9, 11, 13, 15, 17, 22}


def load_source(order: int) -> dict[str, Any]:
    plain = SOURCE / f"order_{order}_delta_3.json"
    zipped = SOURCE / f"order_{order}_delta_3.json.gz"
    if plain.exists():
        with plain.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    if zipped.exists():
        with gzip.open(zipped, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    raise FileNotFoundError(f"Missing source data for order {order}")


def deterministic_indices(total: int, limit: int) -> list[int]:
    """Return deterministic, evenly spread indices, always including endpoints."""
    if total <= limit:
        return list(range(total))
    if limit < 2:
        return [0]
    # Round-to-nearest over [0,total-1]. Deduplicate defensively, then fill gaps.
    span = total - 1
    indices = sorted({round(i * span / (limit - 1)) for i in range(limit)})
    cursor = 0
    while len(indices) < limit:
        if cursor not in indices:
            indices.append(cursor)
        cursor += 1
    return sorted(indices[:limit])


def girth(order: int, edges: list[list[int]]) -> int:
    """Compute the length of the shortest cycle; return 0 if acyclic."""
    adj = [[] for _ in range(order)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    best = order + 1
    for start in range(order):
        dist = [-1] * order
        parent = [-1] * order
        dist[start] = 0
        q: deque[int] = deque([start])
        while q:
            u = q.popleft()
            if dist[u] * 2 + 1 >= best:
                continue
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                elif parent[u] != v and parent[v] != u:
                    best = min(best, dist[u] + dist[v] + 1)
    return 0 if best == order + 1 else best


def degrees(order: int, edges: list[list[int]]) -> list[int]:
    deg = [0] * order
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
    return deg


def compact_record(order: int, source_index: int, survivor: dict[str, Any]) -> dict[str, Any]:
    edges = survivor["edges"]
    deg = degrees(order, edges)
    return {
        "i": source_index,
        "graph6": survivor["graph6"],
        "edges": edges,
        "alpha": survivor["alpha"],
        "girth": girth(order, edges),
        "deg2": [i for i, d in enumerate(deg) if d == 2],
    }


def export() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    index: dict[str, dict[str, Any]] = {}

    for order in ORDERS:
        data = load_source(order)
        survivors = data["survivors"]
        declared = int(data["survivor_count"])
        if declared != len(survivors):
            raise ValueError(
                f"order {order}: survivor_count={declared} but survivors={len(survivors)}"
            )

        if order in FULL_EXPORT_ORDERS:
            selected = list(range(declared))
            sampled = False
        else:
            selected = deterministic_indices(declared, SAMPLE_SIZE)
            sampled = declared > len(selected)

        records = [compact_record(order, idx, survivors[idx]) for idx in selected]
        payload = {
            "order": order,
            "count": declared,
            "available": len(records),
            "sampled": sampled,
            "survivors": records,
        }
        out_path = OUT / f"order_{order}.json"
        out_path.write_text(
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8",
        )
        index[str(order)] = {
            "count": declared,
            "available": len(records),
            "sampled": sampled,
        }

    (OUT / "index.json").write_text(
        json.dumps(index, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )
    return index


def validate(index: dict[str, Any]) -> None:
    total_bytes = 0
    print("Export summary:")
    for path in sorted(OUT.glob("*.json")):
        with path.open("r", encoding="utf-8") as fh:
            obj = json.load(fh)
        size = path.stat().st_size
        total_bytes += size
        if path.name == "index.json":
            print(f"  {path.name}: {size:,} bytes, orders={','.join(obj.keys())}")
            continue
        order = str(obj["order"])
        meta = index[order]
        assert obj["count"] == meta["count"]
        assert obj["available"] == meta["available"] == len(obj["survivors"])
        assert obj["sampled"] == meta["sampled"]
        assert all(isinstance(r["girth"], int) and r["girth"] >= 0 for r in obj["survivors"])
        print(
            f"  {path.name}: {size:,} bytes, count={obj['count']:,}, "
            f"available={obj['available']:,}, sampled={obj['sampled']}"
        )
    print(f"Total JSON payload: {total_bytes:,} bytes ({total_bytes / (1024 * 1024):.2f} MiB)")


def main() -> None:
    index = export()
    validate(index)


if __name__ == "__main__":
    main()
