from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports" / "order19_native_replay_20260728.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_order19_replay_receipt_is_internally_consistent():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    parts = report["parts"]
    aggregate = report["aggregate"]

    assert [part["m"] for part in parts] == list(range(8))
    for key in (
        "read",
        "maxdeg3",
        "val_pass",
        "filt_pass",
        "critical",
        "survivors",
    ):
        assert sum(part[key] for part in parts) == aggregate[key]

    assert aggregate["read"] - aggregate["maxdeg3"] == 1
    assert aggregate["critical"] == report["archived_census"]["critical"]
    assert aggregate["survivors"] == report["archived_census"]["survivors"]


def test_order19_replay_artifact_matches_receipt():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    replay = report["fresh_replay"]
    replay_path = ROOT / replay["file"]

    assert _sha256(replay_path) == replay["file_sha256"]

    digest = hashlib.sha256()
    count = 0
    with gzip.open(replay_path, "rb") as handle:
        for line in handle:
            digest.update(line)
            count += 1

    assert count == report["aggregate"]["survivors"]
    assert digest.hexdigest() == replay["canonical_uncompressed_sha256"]
    assert (
        replay["canonical_uncompressed_sha256"]
        == report["archived_census"]["canonical_survivor_sha256"]
    )
