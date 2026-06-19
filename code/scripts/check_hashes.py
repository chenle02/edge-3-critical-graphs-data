#!/usr/bin/env python3
"""Verify census-result SHA-256 hashes recorded in README.md.

The README's "Census files" markdown table is the source of truth.  Each
table row is expected to contain a backticked filename and a 64-hex SHA-256
digest, for example:

    | `order_13_delta_3.json` | 14 | `799a...ef10` |

This script recomputes the digest of each listed file under --results-dir and
exits nonzero if any file is missing or differs from the recorded digest.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


HASH_RE = re.compile(r"`?([0-9a-fA-F]{64})`?")
FILENAME_RE = re.compile(r"`([^`]+\.(?:json|json\.gz))`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check result-file SHA-256 values against README census table."
    )
    parser.add_argument("--readme", required=True, type=Path, help="Path to README.md")
    parser.add_argument(
        "--results-dir", required=True, type=Path, help="Directory containing result files"
    )
    return parser.parse_args()


def iter_census_table_lines(readme_text: str) -> list[str]:
    """Return markdown table lines under the 'Census files' section."""
    lines = readme_text.splitlines()
    start: int | None = None
    heading_re = re.compile(r"^#{1,6}\s+census files\b", re.IGNORECASE)

    for idx, line in enumerate(lines):
        if heading_re.match(line.strip()):
            start = idx + 1
            break

    if start is None:
        raise ValueError("Could not find a 'Census files' markdown heading")

    table_lines: list[str] = []
    in_table = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#") and in_table:
            break
        if stripped.startswith("|"):
            table_lines.append(stripped)
            in_table = True
            continue
        if in_table and not stripped:
            break

    return table_lines


def parse_expected_hashes(readme: Path) -> list[tuple[str, str]]:
    text = readme.read_text(encoding="utf-8")
    rows: list[tuple[str, str]] = []
    for line in iter_census_table_lines(text):
        filename_match = FILENAME_RE.search(line)
        hash_match = HASH_RE.search(line)
        if filename_match and hash_match:
            rows.append((filename_match.group(1), hash_match.group(1).lower()))
    if not rows:
        raise ValueError("No census filename/SHA-256 rows found in README table")
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def print_results(results: list[tuple[str, str, str, str]]) -> None:
    headers = ("file", "expected", "actual", "status")
    widths = [len(h) for h in headers]
    for row in results:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def fmt(row: tuple[str, str, str, str]) -> str:
        return " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row))

    print(fmt(headers))
    print("-+-".join("-" * width for width in widths))
    for row in results:
        print(fmt(row))


def main() -> int:
    args = parse_args()
    try:
        expected = parse_expected_hashes(args.readme)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    results: list[tuple[str, str, str, str]] = []
    failed = False
    for filename, expected_hash in expected:
        result_path = args.results_dir / filename
        if not result_path.is_file():
            results.append((filename, expected_hash, "-", "MISSING"))
            failed = True
            continue
        actual_hash = sha256_file(result_path)
        status = "OK" if actual_hash == expected_hash else "MISMATCH"
        if status != "OK":
            failed = True
        results.append((filename, expected_hash, actual_hash, status))

    print_results(results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
