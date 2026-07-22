from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "report_computational_effort.py"
SPEC = importlib.util.spec_from_file_location("report_computational_effort", SCRIPT)
assert SPEC and SPEC.loader
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)


def _result(
    path: Path,
    *,
    order: int = 23,
    part: int,
    parts: int = 3,
    processed: int,
    pruned: int,
    noncritical: int,
    critical: int,
    overfull: int,
    survivors: int,
    partial: bool = False,
    interrupted: bool | None = None,
) -> Path:
    suffix = ".partial.json" if partial else ".json"
    # A compact realistic record is enough: production parsing deliberately
    # extracts only scalar metadata from bounded head/tail windows.
    data = {
        "order": order,
        "delta_max": 3,
        "generated_biconnected": processed,
        "processed_graphs": processed,
        "pruned_by_filters": pruned,
        "class1_or_noncritical": noncritical,
        "total_critical": critical,
        "overfull_count": overfull,
        "survivor_count": survivors,
        "survivors": [],
        "runtime_seconds": 123.5,
        "interrupted": partial if interrupted is None else interrupted,
        "generation_complete": not partial,
        "mod_split": {"m": part, "N": parts},
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def _log(
    path: Path, job: str, part: int, parts: int = 3,
    secret: str = "private-user@private-node",
) -> None:
    path.write_text(
        f"ORDER=23\nM_SLICE={part}\nN_PARTS={parts}\njob={job}\n"
        f"account={secret}\ncommand=/scratch/{secret}/run\n",
        encoding="utf-8",
    )


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    results = tmp_path / "results"
    logs = tmp_path / "logs"
    results.mkdir()
    logs.mkdir()

    # Padded final wins over an older unpadded partial for part 0.
    _result(
        results / "order_23_delta_3_part00of3.json",
        part=0, processed=100, pruned=10, noncritical=70,
        critical=20, overfull=18, survivors=2,
    )
    _result(
        results / "order_23_delta_3_part0of3.partial.json",
        part=0, processed=50, pruned=5, noncritical=35,
        critical=10, overfull=9, survivors=1, partial=True,
    )
    # Unpadded final with one explicitly represented unclassified graph.
    _result(
        results / "order_23_delta_3_part1of3.json",
        part=1, processed=81, pruned=10, noncritical=60,
        critical=10, overfull=9, survivors=1,
    )
    _result(
        results / "order_23_delta_3_part02of3.partial.json",
        part=2, processed=40, pruned=5, noncritical=30,
        critical=5, overfull=4, survivors=1, partial=True, interrupted=False,
    )

    _log(logs / "run-100001_0.out", "100001_0", 0)
    _log(logs / "retry-100002_0.out", "100002_0", 0)
    _log(logs / "run-100003_1.out", "100003_1", 1)
    _log(logs / "run-100004_2.out", "100004_2", 2)

    sacct = tmp_path / "sacct.psv"
    sacct.write_text(
        "JobIDRaw|JobID|State|Start|End|ElapsedRaw|AllocCPUS|\n"
        "100001_0|100001_0|FAILED|2026-01-02T01:00:00|2026-01-02T01:01:00|60|2|\n"
        # Step rows must not be double-counted.
        "100001.0|100001_0.batch|FAILED|2026-01-02T01:00:00|2026-01-02T01:01:00|60|2|\n"
        "100002_0|100002_0|COMPLETED|2026-01-01T00:00:00|2026-01-03T00:00:00|120|4|\n"
        "100003_1|100003_1|TIMEOUT|2026-01-04T00:00:00|2026-01-04T00:05:00|300|3|\n"
        "100004_2|100004_2|RUNNING|2026-01-05T00:00:00|Unknown|180|8|\n",
        encoding="utf-8",
    )
    return results, logs, sacct


def test_collect_retries_states_mixed_cpus_and_privacy(tmp_path: Path) -> None:
    results, logs, sacct = _fixture(tmp_path)
    prefix = tmp_path / "effort"
    exit_code = report.main([
        "collect", "--order", "23", "--parts", "3",
        "--results-dir", str(results), "--logs-dir", str(logs),
        "--sacct-file", str(sacct), "--generated-at", "2026-01-06T00:00:00Z",
        "--output-prefix", str(prefix),
    ])
    assert exit_code == 0

    snapshot = json.loads(prefix.with_suffix(".json").read_text(encoding="utf-8"))
    rows = snapshot["slices"]
    assert snapshot["provisional"] is True
    assert snapshot["complete_parts"] == 2
    assert snapshot["slurm_timezone"] == "America/Chicago"
    assert snapshot["campaign_start"] == "2026-01-01T00:00:00"
    assert snapshot["campaign_end"] is None
    assert rows[0]["result_kind"] == "final"
    assert rows[0]["processed"] == 100  # final preferred over partial
    assert rows[0]["attempts"] == 2
    assert rows[0]["attempt_states"] == {"COMPLETED": 1, "FAILED": 1}
    assert rows[0]["earliest_start"] == "2026-01-01T00:00:00"
    assert rows[0]["latest_end"] == "2026-01-03T00:00:00"
    assert rows[0]["slurm_wall_seconds"] == 180
    assert rows[0]["allocated_core_hours"] == pytest.approx((60 * 2 + 120 * 4) / 3600)
    assert rows[1]["unclassified"] == 1
    assert rows[1]["attempt_states"] == {"TIMEOUT": 1}
    assert rows[2]["attempt_states"] == {"RUNNING": 1}
    assert rows[2]["latest_end"] is None
    assert rows[2]["allocated_core_hours"] == pytest.approx(180 * 8 / 3600)

    all_output = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (prefix.with_suffix(".json"), prefix.with_suffix(".tsv"), prefix.with_suffix(".md"))
    )
    assert "private-user" not in all_output
    assert "private-node" not in all_output
    assert "/scratch/" not in all_output
    assert "account=" not in all_output
    assert "job_ids" not in all_output
    assert "100001_0" not in all_output
    assert all("job_ids" not in row for row in rows)
    markdown = prefix.with_suffix(".md").read_text(encoding="utf-8")
    assert report.ACKNOWLEDGMENT in markdown
    assert "Campaign start: 2026-01-01T00:00:00 (America/Chicago)" in markdown
    assert "Campaign end: running at snapshot 2026-01-06T00:00:00Z" in markdown
    assert "Start (America/Chicago)" in markdown
    assert "End (America/Chicago)" in markdown
    assert "running / unknown" in markdown


def test_completed_campaign_uses_latest_terminal_end(tmp_path: Path) -> None:
    results, logs, sacct = _fixture(tmp_path)
    result_rows = report.discover_results(results, 23, 3)
    job_parts = report.discover_job_parts(logs, 23, 3)
    attempts = report.aggregate_attempts(report.collect_sacct(job_parts, sacct), job_parts, 3)
    result_rows[2]["result_kind"] = "final"
    attempts[2]["running"] = False
    attempts[2]["latest_end"] = "2026-01-07T12:00:00"
    attempts[2]["attempt_states"] = {"COMPLETED": 1}

    snapshot = report.build_snapshot(
        23, 3, result_rows, attempts, "2026-01-08T00:00:00Z", "UTC"
    )
    assert snapshot["provisional"] is False
    assert snapshot["campaign_end"] == "2026-01-07T12:00:00"
    markdown = report.render_markdown(snapshot)
    assert "Campaign end: 2026-01-07T12:00:00 (UTC)" in markdown
    assert "running at snapshot" not in markdown


def test_snapshot_rerender_is_byte_deterministic(tmp_path: Path) -> None:
    results, logs, sacct = _fixture(tmp_path)
    first = tmp_path / "first"
    second = tmp_path / "second"
    assert report.main([
        "collect", "--order", "23", "--parts", "3",
        "--results-dir", str(results), "--logs-dir", str(logs),
        "--sacct-file", str(sacct), "--generated-at", "2026-01-06T00:00:00Z",
        "--output-prefix", str(first),
    ]) == 0
    assert report.main([
        "render", "--snapshot", str(first.with_suffix(".json")),
        "--output-prefix", str(second),
    ]) == 0
    for suffix in (".json", ".tsv", ".md"):
        assert first.with_suffix(suffix).read_bytes() == second.with_suffix(suffix).read_bytes()


def test_log_filename_job_id_overrides_misleading_slice_header(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "cgaDarr-5234306_4.out").write_text(
        "ORDER=23\nM_SLICE=16\nN_PARTS=64\njob=5234306_16\n",
        encoding="utf-8",
    )

    assert report.discover_job_parts(logs, 23, 64) == {"5234306_4": 16}


def test_log_discovery_skips_mixed_partition_campaigns(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    _log(logs / "order23-600001_0.out", "600001_0", 0, parts=64)
    _log(logs / "order23-600002_0.out", "600002_0", 0, parts=32)

    assert report.discover_job_parts(logs, 23, 64) == {"600001_0": 0}


def test_result_flags_and_small_modular_identity_fail_closed(tmp_path: Path) -> None:
    incomplete = _result(
        tmp_path / "order_23_delta_3_part0of1.json", parts=1, part=0,
        processed=10, pruned=1, noncritical=8, critical=1, overfull=1, survivors=0,
    )
    data = json.loads(incomplete.read_text(encoding="utf-8"))
    data["generation_complete"] = False
    data["interrupted"] = True
    incomplete.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="final result has incomplete/interrupted flags"):
        report.parse_result(incomplete, 23, 1)

    mismatched = _result(
        tmp_path / "order_23_delta_3_part0of2.partial.json", parts=2, part=0,
        processed=10, pruned=1, noncritical=8, critical=1, overfull=1, survivors=0,
        partial=True,
    )
    data = json.loads(mismatched.read_text(encoding="utf-8"))
    data["mod_split"] = {"m": 1, "N": 2}
    mismatched.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="modular identity conflicts"):
        report.parse_result(mismatched, 23, 2)


def test_slurm_state_suffixes_reasons_and_unknown_states() -> None:
    def row(state: str, end: str = "Unknown") -> dict[str, str]:
        return {
            "JobIDRaw": "700001_0", "JobID": "700001_0", "State": state,
            "Start": "2026-01-01T00:00:00", "End": end,
            "ElapsedRaw": "60", "AllocCPUS": "2",
        }

    live = report.aggregate_attempts([row("STAGE_OUT+")], {"700001_0": 0}, 1)[0]
    assert live["running"] is True
    assert live["latest_end"] is None
    assert live["attempt_states"] == {"STAGE_OUT": 1}

    stopped = report.aggregate_attempts([row("STOPPED")], {"700001_0": 0}, 1)[0]
    assert stopped["running"] is True
    assert stopped["latest_end"] is None

    terminal = report.aggregate_attempts(
        [row("CANCELLED by 700000", "2026-01-01T00:01:00")],
        {"700001_0": 0}, 1,
    )[0]
    assert terminal["running"] is False
    assert terminal["attempt_states"] == {"CANCELLED": 1}
    assert terminal["latest_end"] == "2026-01-01T00:01:00"

    with pytest.raises(ValueError, match="unknown Slurm states: FUTURE_STATE"):
        report.aggregate_attempts([row("FUTURE_STATE")], {"700001_0": 0}, 1)


def test_large_result_reads_only_bounded_head_and_tail(tmp_path: Path) -> None:
    valid = tmp_path / "order_23_delta_3_part0of1.json"
    head = (
        '{"order":23,"generated_biconnected":10,"processed_graphs":10,'
        '"pruned_by_filters":1,"class1_or_noncritical":8,"total_critical":1,'
        '"overfull_count":1,"survivor_count":0,"survivors":['
    )
    tail = (
        '],"runtime_seconds":123.5,"interrupted":false,'
        '"generation_complete":true,"mod_split":{"m":0,"N":1}}'
    )
    valid.write_text(
        head + ("0," * (report.WINDOW_BYTES + 1)) + "0" + tail,
        encoding="utf-8",
    )
    assert valid.stat().st_size > 2 * report.WINDOW_BYTES
    assert report.parse_result(valid, 23, 1)["processed"] == 10

    hidden = tmp_path / "order_23_delta_3_part00of1.json"
    before = (
        '{"order":23,"generated_biconnected":10,"processed_graphs":10,'
        '"pruned_by_filters":1,"class1_or_noncritical":8,"total_critical":1,'
        '"overfull_count":1,"survivor_count":0,"pad1":"'
        + ("x" * (report.WINDOW_BYTES + 100))
        + '","runtime_seconds":123.5,"pad2":"'
    )
    after = (
        ("y" * (report.WINDOW_BYTES + 100))
        + '","interrupted":false,"generation_complete":true,'
        '"mod_split":{"m":0,"N":1}}'
    )
    hidden.write_text(before + after, encoding="utf-8")
    assert hidden.stat().st_size > 2 * report.WINDOW_BYTES
    with pytest.raises(ValueError, match="missing scalar field 'runtime_seconds'"):
        report.parse_result(hidden, 23, 1)


def test_duplicate_conflicting_final_results_are_rejected(tmp_path: Path) -> None:
    results = tmp_path / "results"
    results.mkdir()
    _result(
        results / "order_23_delta_3_part0of1.json", parts=1, part=0,
        processed=10, pruned=1, noncritical=8, critical=1, overfull=1, survivors=0,
    )
    _result(
        results / "order_23_delta_3_part00of1.json", parts=1, part=0,
        processed=11, pruned=1, noncritical=9, critical=1, overfull=1, survivors=0,
    )
    with pytest.raises(ValueError, match="duplicate conflicting final"):
        report.discover_results(results, 23, 1)


def test_validation_rejects_live_end_and_bad_accounting(tmp_path: Path) -> None:
    results, logs, sacct = _fixture(tmp_path)
    result_rows = report.discover_results(results, 23, 3)
    job_parts = report.discover_job_parts(logs, 23, 3)
    attempts = report.aggregate_attempts(report.collect_sacct(job_parts, sacct), job_parts, 3)
    snapshot = report.build_snapshot(23, 3, result_rows, attempts, "2026-01-06T00:00:00Z")

    snapshot["slices"][2]["latest_end"] = "2026-01-06T00:00:00"
    with pytest.raises(ValueError, match="live row"):
        report.validate_snapshot(snapshot)
    snapshot["slices"][2]["latest_end"] = None
    snapshot["slices"][0]["job_ids"] = ["700001_0"]
    with pytest.raises(ValueError, match="raw job IDs are prohibited"):
        report.validate_snapshot(snapshot)
    del snapshot["slices"][0]["job_ids"]
    snapshot["slices"][1]["processed"] += 1
    with pytest.raises(ValueError, match="does not balance"):
        report.validate_snapshot(snapshot)
