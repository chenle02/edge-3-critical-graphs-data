#!/usr/bin/env python3
"""Build reproducible, privacy-safe computational-effort reports for a census.

Collection reads only bounded windows of result files.  A saved snapshot is the
canonical input for deterministic re-rendering; it deliberately contains no
filesystem, user, host, command, or Slurm-account information.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ACKNOWLEDGMENT = (
    "This work was completed in part with resources provided by the Auburn "
    "University Easley Cluster."
)
SCHEMA_VERSION = 1
WINDOW_BYTES = 256 * 1024
TERMINAL_STATES = {
    "BOOT_FAIL", "CANCELLED", "COMPLETED", "DEADLINE", "FAILED", "NODE_FAIL",
    "OUT_OF_MEMORY", "PREEMPTED", "REVOKED", "SPECIAL_EXIT", "TIMEOUT",
}
LIVE_STATES = {
    "COMPLETING", "CONFIGURING", "PENDING", "REQUEUED", "REQUEUE_FED",
    "REQUEUE_HOLD", "RESIZING", "RUNNING", "SIGNALING", "STAGE_OUT", "STOPPED",
    "SUSPENDED",
}
RESULT_RE = re.compile(
    r"^order_(?P<order>\d+)_delta_\d+_part(?P<part>\d+)of(?P<parts>\d+)"
    r"(?P<partial>\.partial)?\.json$"
)
SCALAR_KEYS = {
    "order", "generated_biconnected", "processed_graphs", "pruned_by_filters",
    "class1_or_noncritical", "total_critical", "overfull_count", "survivor_count",
    "runtime_seconds", "interrupted", "generation_complete",
}


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _iso_mtime(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")


def _read_windows(path: Path, window: int = WINDOW_BYTES) -> tuple[str, str]:
    """Read bounded head/tail byte windows, never an entire large result file."""
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(min(window, size))
        if size > window:
            handle.seek(max(window, size - window))
            tail = handle.read(window)
        else:
            tail = b""
    return head.decode("utf-8", "replace"), tail.decode("utf-8", "replace")


def _json_scalar(text: str, key: str) -> Any:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*(null|true|false|-?\d+(?:\.\d+)?)', text)
    if not match:
        raise ValueError(f"result is missing scalar field {key!r} in bounded windows")
    value = match.group(1)
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    return float(value) if "." in value else int(value)


def parse_result(path: Path, order: int, parts: int) -> dict[str, Any]:
    match = RESULT_RE.match(path.name)
    if not match:
        raise ValueError(f"unsupported result filename: {path.name}")
    identity = {k: int(match.group(k)) for k in ("order", "part", "parts")}
    if identity["order"] != order or identity["parts"] != parts:
        raise ValueError(f"result identity conflicts with requested census: {path.name}")
    head, tail = _read_windows(path)
    text = head + "\n" + tail
    values = {key: _json_scalar(text, key) for key in SCALAR_KEYS}
    if values["order"] != order:
        raise ValueError(f"JSON order conflicts with filename: {path.name}")
    mod_match = re.search(r'"mod_split"\s*:\s*\{(?P<body>[^{}]*)\}', text)
    if not mod_match:
        raise ValueError(f"result is missing mod_split identity in bounded windows: {path.name}")
    mod_identity = (
        _json_scalar(mod_match.group("body"), "m"),
        _json_scalar(mod_match.group("body"), "N"),
    )
    if mod_identity != (identity["part"], parts):
        raise ValueError(f"JSON modular identity conflicts with filename: {path.name}")
    result_kind = "partial" if match.group("partial") else "final"
    if result_kind == "final" and (
        values["generation_complete"] is not True or values["interrupted"] is not False
    ):
        raise ValueError(f"final result has incomplete/interrupted flags: {path.name}")
    if result_kind == "partial" and values["generation_complete"] is not False:
        raise ValueError(f"partial result is marked generation-complete: {path.name}")
    processed = int(values["processed_graphs"])
    pruned = int(values["pruned_by_filters"])
    noncritical = int(values["class1_or_noncritical"])
    critical = int(values["total_critical"])
    return {
        "part": identity["part"],
        "result_kind": result_kind,
        "result_timestamp": _iso_mtime(path),
        "processed": processed,
        "pruned": pruned,
        "noncritical": noncritical,
        "critical": critical,
        "overfull": int(values["overfull_count"]),
        "survivors": int(values["survivor_count"]),
        "unclassified": processed - pruned - noncritical - critical,
        "json_runtime_seconds": float(values["runtime_seconds"]),
    }


def discover_results(results_dir: Path, order: int, parts: int) -> dict[int, dict[str, Any]]:
    candidates: dict[int, dict[str, list[dict[str, Any]]]] = {}
    for path in sorted(results_dir.iterdir()):
        match = RESULT_RE.match(path.name)
        if not match or int(match.group("order")) != order or int(match.group("parts")) != parts:
            continue
        row = parse_result(path, order, parts)
        bucket = candidates.setdefault(row["part"], {"final": [], "partial": []})
        bucket[row["result_kind"]].append(row)
    found: dict[int, dict[str, Any]] = {}
    for part, kinds in candidates.items():
        selected_kind = "final" if kinds["final"] else "partial"
        rows = kinds[selected_kind]
        identities = {
            tuple((key, json.dumps(value, sort_keys=True)) for key, value in sorted(row.items()) if key != "result_timestamp")
            for row in rows
        }
        if len(identities) > 1:
            raise ValueError(f"duplicate conflicting {selected_kind} results for part {part}")
        found[part] = max(rows, key=lambda row: row["result_timestamp"])
    missing = sorted(set(range(parts)) - set(found))
    extra = sorted(set(found) - set(range(parts)))
    if missing or extra:
        raise ValueError(f"expected parts exactly 0..{parts - 1}; missing={missing}, extra={extra}")
    return found


def _bounded_log_header(path: Path) -> str:
    with path.open("rb") as handle:
        return handle.read(128 * 1024).decode("utf-8", "replace")


def discover_job_parts(logs_dir: Path, order: int, parts: int) -> dict[str, int]:
    """Map top-level Slurm job IDs to census parts using log headers/names."""
    mapping: dict[str, int] = {}
    for path in sorted(p for p in logs_dir.iterdir() if p.is_file()):
        text = _bounded_log_header(path)
        order_matches = [
            re.search(rf"\bORDER\s*=\s*{order}\b", text, re.I),
            re.search(rf"--orders?\s+{order}\b", text),
            re.search(rf"\border[ =_-]+{order}\b", text, re.I),
            re.search(rf"\bn\s*=\s*{order}\b", text, re.I),
        ]
        if not any(order_matches):
            continue
        part_match = (
            re.search(r"\bM_(?:SLICE|PART)\s*=\s*(\d+)\b", text, re.I)
            or re.search(r"(?:--)?geng-mod(?:\s+|\s*=\s*)(\d+)/(\d+)", text, re.I)
            or re.search(r"\bpart[ =_-]?(\d+)(?:/|of)(\d+)\b", text, re.I)
        )
        denominators = {
            int(value)
            for pattern in (
                r"\bN_PARTS\s*=\s*(\d+)\b",
                r"(?:--)?geng-mod(?:\s+|\s*=\s*)\d+/(\d+)",
                r"\bpart[ =_-]?\d+(?:/|of)(\d+)\b",
            )
            for value in re.findall(pattern, text, re.I)
        }
        if not part_match or not denominators:
            continue
        if denominators != {parts}:
            continue
        part = int(part_match.group(1))
        if part < 0 or part >= parts:
            raise ValueError(f"log contains out-of-range part {part}: {path.name}")
        job_match = (
            re.search(r"(?<!\d)(\d{5,}(?:_\d+)?)(?!\d)", path.name)
            or re.search(r"\b(?:SLURM_(?:ARRAY_)?JOB_ID|job)\s*=\s*(\d+(?:_\d+)?)\b", text, re.I)
        )
        if not job_match:
            continue
        job_id = job_match.group(1)
        previous = mapping.get(job_id)
        if previous is not None and previous != part:
            raise ValueError(f"job {job_id} maps to conflicting parts {previous} and {part}")
        mapping[job_id] = part
    if not mapping:
        raise ValueError("no census job identities were discovered in log headers")
    return mapping


def _sacct_command(job_roots: Iterable[str]) -> list[str]:
    fields = "JobIDRaw,JobID,State,Start,End,ElapsedRaw,AllocCPUS"
    return ["sacct", "-n", "-P", "-X", "-j", ",".join(sorted(job_roots)), f"--format={fields}"]


def read_sacct(text: str) -> list[dict[str, str]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("sacct data is empty")
    expected = ["JobIDRaw", "JobID", "State", "Start", "End", "ElapsedRaw", "AllocCPUS"]
    first = lines[0].rstrip("|").split("|")
    if first == expected:
        data_lines = lines[1:]
    else:
        data_lines = lines
    rows = []
    for line in data_lines:
        fields = line.rstrip("|").split("|")
        if len(fields) != len(expected):
            raise ValueError(f"malformed sacct row: expected {len(expected)} fields")
        rows.append(dict(zip(expected, fields)))
    return rows


def collect_sacct(job_parts: dict[str, int], sacct_file: Path | None) -> list[dict[str, str]]:
    roots = {job_id.split("_", 1)[0] for job_id in job_parts}
    if sacct_file:
        text = sacct_file.read_text(encoding="utf-8")
    else:
        proc = subprocess.run(_sacct_command(roots), check=True, text=True, capture_output=True)
        text = proc.stdout
    return read_sacct(text)


def _clean_state(state: str) -> str:
    return state.strip().split()[0].split("+")[0].upper()


def aggregate_attempts(
    sacct_rows: list[dict[str, str]], job_parts: dict[str, int], parts: int
) -> dict[int, dict[str, Any]]:
    grouped: dict[int, list[dict[str, str]]] = {part: [] for part in range(parts)}
    for row in sacct_rows:
        job_id = row["JobID"].strip() or row["JobIDRaw"].strip()
        if "." in job_id:  # Never double count batch/extern/step records.
            continue
        part = job_parts.get(job_id)
        if part is None:
            continue
        grouped[part].append(row)
    output: dict[int, dict[str, Any]] = {}
    for part, rows in grouped.items():
        if not rows:
            raise ValueError(f"no sacct attempt record found for part {part}")
        # One top-level record per job identity; identical duplicates are ignored.
        unique: dict[str, dict[str, str]] = {}
        for row in rows:
            job_id = row["JobID"].strip() or row["JobIDRaw"].strip()
            prior = unique.get(job_id)
            if prior is not None and prior != row:
                raise ValueError(f"conflicting sacct records for job {job_id}")
            unique[job_id] = row
        rows = list(unique.values())
        states = Counter(_clean_state(row["State"]) for row in rows)
        unknown_states = sorted(set(states) - TERMINAL_STATES - LIVE_STATES)
        if unknown_states:
            raise ValueError(
                f"part {part} has unknown Slurm states: {', '.join(unknown_states)}"
            )
        is_live = any(state in LIVE_STATES for state in states)
        starts = [row["Start"] for row in rows if row["Start"] not in ("", "Unknown", "N/A")]
        ends = [row["End"] for row in rows if row["End"] not in ("", "Unknown", "N/A")]
        wall = sum(int(row["ElapsedRaw"] or 0) for row in rows)
        cpu_seconds = sum(int(row["ElapsedRaw"] or 0) * int(row["AllocCPUS"] or 0) for row in rows)
        output[part] = {
            "attempts": len(rows),
            "attempt_states": dict(sorted(states.items())),
            "earliest_start": min(starts) if starts else None,
            "latest_end": None if is_live else (max(ends) if ends else None),
            "slurm_wall_seconds": wall,
            "allocated_core_hours": cpu_seconds / 3600,
            "running": is_live,
        }
    return output


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported snapshot schema version")
    if not isinstance(snapshot.get("slurm_timezone"), str) or not snapshot["slurm_timezone"]:
        raise ValueError("slurm_timezone must be a nonempty string")
    parts = int(snapshot["parts"])
    rows = snapshot["slices"]
    identities = [int(row["part"]) for row in rows]
    if identities != list(range(parts)):
        raise ValueError(f"expected parts exactly 0..{parts - 1}")
    for row in rows:
        if "job_ids" in row:
            raise ValueError(f"part {row['part']}: raw job IDs are prohibited in snapshots")
        counters = [row[key] for key in ("processed", "pruned", "noncritical", "critical", "overfull", "survivors", "unclassified")]
        if any(not isinstance(value, int) or value < 0 for value in counters):
            raise ValueError(f"part {row['part']} has a negative or non-integer counter")
        if row["critical"] != row["overfull"] + row["survivors"]:
            raise ValueError(f"part {row['part']}: critical != overfull + survivors")
        classified = row["pruned"] + row["noncritical"] + row["critical"] + row["unclassified"]
        if row["processed"] != classified:
            raise ValueError(f"part {row['part']}: processed accounting does not balance")
        if row["running"] and row["latest_end"] is not None:
            raise ValueError(f"part {row['part']}: a live row must have null latest_end")
        if row["result_kind"] == "final" and row["running"]:
            raise ValueError(f"part {row['part']}: final result cannot have a live attempt")
    expected_complete = sum(row["result_kind"] == "final" for row in rows)
    if snapshot["complete_parts"] != expected_complete:
        raise ValueError("complete_parts does not match result kinds")
    expected_provisional = any(
        row["result_kind"] != "final" or row["running"] for row in rows
    )
    if snapshot["provisional"] != expected_provisional:
        raise ValueError("provisional does not match slice states")
    starts = [row["earliest_start"] for row in rows if row["earliest_start"]]
    ends = [row["latest_end"] for row in rows if row["latest_end"]]
    if snapshot["campaign_start"] != (min(starts) if starts else None):
        raise ValueError("campaign_start does not match slice attempts")
    expected_end = None if expected_provisional else (max(ends) if ends else None)
    if snapshot["campaign_end"] != expected_end:
        raise ValueError("campaign_end does not match slice states")


def build_snapshot(
    order: int, parts: int, results: dict[int, dict[str, Any]],
    attempts: dict[int, dict[str, Any]], generated_at: str,
    slurm_timezone: str = "America/Chicago",
) -> dict[str, Any]:
    rows = []
    for part in range(parts):
        row = dict(results[part])
        row.update(attempts[part])
        rows.append(row)
    provisional = any(row["result_kind"] != "final" or row["running"] for row in rows)
    starts = [row["earliest_start"] for row in rows if row["earliest_start"]]
    ends = [row["latest_end"] for row in rows if row["latest_end"]]
    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "slurm_timezone": slurm_timezone,
        "campaign_start": min(starts) if starts else None,
        "campaign_end": None if provisional else (max(ends) if ends else None),
        "order": order,
        "parts": parts,
        "complete_parts": sum(row["result_kind"] == "final" for row in rows),
        "provisional": provisional,
        "acknowledgment": ACKNOWLEDGMENT,
        "slices": rows,
    }
    validate_snapshot(snapshot)
    return snapshot


def _fmt_int(value: int) -> str:
    return f"{value:,}"


def _fmt_duration(seconds: int) -> str:
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{days}d {hours:02d}:{minutes:02d}:{secs:02d}"


def _totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = ("processed", "pruned", "noncritical", "critical", "overfull", "survivors", "unclassified", "attempts", "slurm_wall_seconds")
    totals = {key: sum(row[key] for row in rows) for key in keys}
    totals["allocated_core_hours"] = sum(row["allocated_core_hours"] for row in rows)
    return totals


def render_markdown(snapshot: dict[str, Any]) -> str:
    validate_snapshot(snapshot)
    rows = snapshot["slices"]
    totals = _totals(rows)
    status = "PROVISIONAL / INCOMPLETE" if snapshot["provisional"] else "COMPLETE"
    campaign_end = snapshot["campaign_end"] or f"running at snapshot {snapshot['generated_at']}"
    timezone = snapshot["slurm_timezone"]
    lines = [
        f"# Order {snapshot['order']} computational effort",
        "", f"**Status: {status}.** Snapshot generated {snapshot['generated_at']}.", "",
        "## Run interval", "",
        f"- Campaign start: {snapshot['campaign_start'] or 'unknown'} ({timezone})",
        f"- Campaign end: {campaign_end}" + (f" ({timezone})" if snapshot["campaign_end"] else ""),
        f"- Slurm timestamp timezone: `{timezone}`",
        f"- Completed slices: {snapshot['complete_parts']}/{snapshot['parts']}", "",
        "## Per-slice statistics", "",
        f"| Part | Result | Processed | Pruned | Noncritical | Critical | Overfull | Survivors | Unclassified | Attempts / states | Start ({timezone}) | End ({timezone}) | Slurm wall | Core-hours |",
        "|---:|:---|---:|---:|---:|---:|---:|---:|---:|:---|:---|:---|---:|---:|",
    ]
    for row in rows:
        states = ", ".join(f"{key}:{value}" for key, value in row["attempt_states"].items())
        result = row["result_kind"] + (" (running)" if row["running"] else "")
        lines.append(
            f"| {row['part']} | {result} | {_fmt_int(row['processed'])} | {_fmt_int(row['pruned'])} | "
            f"{_fmt_int(row['noncritical'])} | {_fmt_int(row['critical'])} | {_fmt_int(row['overfull'])} | "
            f"{_fmt_int(row['survivors'])} | {_fmt_int(row['unclassified'])} | {row['attempts']} / {states} | "
            f"{row['earliest_start'] or 'unknown'} | {row['latest_end'] or 'running / unknown'} | "
            f"{_fmt_duration(row['slurm_wall_seconds'])} | {row['allocated_core_hours']:,.3f} |"
        )
    lines.extend(["", "## Totals", ""])
    for key, label in (
        ("processed", "Processed graphs"), ("pruned", "Pruned"),
        ("noncritical", "Class-1/noncritical"), ("critical", "Critical"),
        ("overfull", "Overfull"), ("survivors", "Survivors"),
        ("unclassified", "Unclassified remainder"), ("attempts", "Slurm attempts"),
    ):
        lines.append(f"- {label}: {_fmt_int(totals[key])}")
    lines += [
        f"- Cumulative Slurm wall time: {_fmt_duration(totals['slurm_wall_seconds'])}",
        f"- Allocated compute: {totals['allocated_core_hours']:,.3f} core-hours", "",
        "## Rankings and outliers", "",
    ]
    for key, label in (("processed", "Processed graphs"), ("critical", "Critical graphs"), ("survivors", "Survivors"), ("slurm_wall_seconds", "Cumulative Slurm wall time"), ("allocated_core_hours", "Allocated compute")):
        ranked = sorted(rows, key=lambda row: (-row[key], row["part"]))[:5]
        lines.append(f"- **{label}:** " + "; ".join(f"part {row['part']} ({row[key]:,.3f})" if isinstance(row[key], float) else f"part {row['part']} ({row[key]:,})" for row in ranked))
    retry_parts = [row for row in rows if row["attempts"] > 1]
    unclassified = [row for row in rows if row["unclassified"]]
    unclassified_text = ", ".join(
        f"part {row['part']} ({row['unclassified']})" for row in unclassified
    )
    lines += [
        f"- **Retried slices:** {', '.join(str(row['part']) for row in retry_parts) or 'none'}.",
        f"- **Nonzero unclassified remainder:** {unclassified_text or 'none'}.",
        "", "## Definitions and caveats", "",
        "- `processed = pruned + noncritical + critical + unclassified`; the unclassified remainder makes category-accounting gaps explicit.",
        "- `critical = overfull + survivors` is checked for every slice.",
        "- Slurm wall time is cumulative `ElapsedRaw` over top-level attempts, including failed, timed-out, and running attempts; it is not calendar duration.",
        "- Allocated core-hours sum `ElapsedRaw × AllocCPUS / 3600` per attempt, so retries and mixed CPU allocations are represented.",
        "- JSON `runtime_seconds` is retained in the machine-readable snapshot but is not substituted for cumulative Slurm effort.",
        "- A running slice has no end date. Partial counters are censored and must not be interpreted as the slice's final size.",
        "- The snapshot contains curated per-slice provenance only: no source paths, user/account names, hosts/nodes, commands, or log streams.",
        "", "## Acknowledgment", "", ACKNOWLEDGMENT, "",
    ]
    return "\n".join(lines)


def render_tsv(snapshot: dict[str, Any]) -> str:
    validate_snapshot(snapshot)
    fields = [
        "part", "result_kind", "running", "processed", "pruned", "noncritical", "critical",
        "overfull", "survivors", "unclassified", "result_timestamp", "attempts",
        "attempt_states", "earliest_start", "latest_end", "slurm_wall_seconds",
        "allocated_core_hours", "json_runtime_seconds",
    ]
    from io import StringIO
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in snapshot["slices"]:
        values = {key: row[key] for key in fields}
        values["attempt_states"] = json.dumps(values["attempt_states"], sort_keys=True, separators=(",", ":"))
        writer.writerow(values)
    return stream.getvalue()


def write_outputs(snapshot: dict[str, Any], output_prefix: Path, write_snapshot: bool = True) -> None:
    validate_snapshot(snapshot)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    if write_snapshot:
        output_prefix.with_suffix(".json").write_text(
            json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    output_prefix.with_suffix(".tsv").write_text(render_tsv(snapshot), encoding="utf-8")
    output_prefix.with_suffix(".md").write_text(render_markdown(snapshot), encoding="utf-8")


def _collect(args: argparse.Namespace) -> None:
    results = discover_results(args.results_dir, args.order, args.parts)
    jobs = discover_job_parts(args.logs_dir, args.order, args.parts)
    attempts = aggregate_attempts(collect_sacct(jobs, args.sacct_file), jobs, args.parts)
    snapshot = build_snapshot(
        args.order, args.parts, results, attempts, args.generated_at or _utc_now(),
        args.slurm_timezone,
    )
    write_outputs(snapshot, args.output_prefix)


def _render(args: argparse.Namespace) -> None:
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    write_outputs(snapshot, args.output_prefix)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect", help="collect results and Slurm accounting")
    collect.add_argument("--order", type=int, required=True)
    collect.add_argument("--parts", type=int, required=True)
    collect.add_argument("--results-dir", type=Path, required=True)
    collect.add_argument("--logs-dir", type=Path, required=True)
    collect.add_argument("--sacct-file", type=Path, help="saved parsable sacct output; omit for a live query")
    collect.add_argument("--generated-at", help="ISO snapshot timestamp (useful for reproducible archival collection)")
    collect.add_argument(
        "--slurm-timezone", default="America/Chicago",
        help="IANA timezone for sacct Start/End timestamps (default: America/Chicago)",
    )
    collect.add_argument("--output-prefix", type=Path, required=True)
    collect.set_defaults(func=_collect)
    render = subparsers.add_parser("render", help="deterministically re-render a sanitized snapshot")
    render.add_argument("--snapshot", type=Path, required=True)
    render.add_argument("--output-prefix", type=Path, required=True)
    render.set_defaults(func=_render)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
