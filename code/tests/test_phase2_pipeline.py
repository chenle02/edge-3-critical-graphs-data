from __future__ import annotations

import io
import json
import os
import signal
import subprocess
from pathlib import Path

import networkx as nx
import pytest

import main as search_main


def _g6(graph: nx.Graph) -> str:
  return nx.to_graph6_bytes(graph, header=False).decode("ascii").strip()


def _fingerprint_prefix(graphs: list[str]) -> str:
  fingerprint = "00" * 32
  for g6 in graphs:
    fingerprint = search_main._update_prefix_fingerprint(fingerprint, g6)
  return fingerprint


def test_process_graph_accepts_density_implementation_reference_and_fast(monkeypatch):
  monkeypatch.setattr(search_main, "passes_all_filters", lambda G: True)
  monkeypatch.setattr(search_main, "is_delta_critical", lambda G: True)

  g6 = _g6(nx.complete_graph(5))

  reference = search_main._process_graph((g6, 4, "reference"))
  fast = search_main._process_graph((g6, 4, "fast"))

  assert reference == {"status": "overfull"}
  assert fast == reference


def test_analyze_order_respects_limit_graphs_and_density_implementation(monkeypatch):
  graphs = [
    _g6(nx.cycle_graph(5)),
    _g6(nx.cycle_graph(6)),
    _g6(nx.complete_graph(4)),
  ]

  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: graphs)
  monkeypatch.setattr(search_main, "passes_all_filters", lambda G: True)
  monkeypatch.setattr(search_main, "is_delta_critical", lambda G: True)

  result = search_main.analyze_order(
    6,
    delta=2,
    workers=1,
    min_degree=2,
    density_implementation="fast",
    limit_graphs=2,
  )

  assert result["generated_biconnected"] == 2
  assert result["processed_graphs"] == 2
  assert result["total_critical"] == 2
  assert result["overfull_count"] == 1
  assert result["survivor_count"] == 1
  assert result["class1_or_noncritical"] == 0
  assert result["interrupted"] is False


def test_analyze_order_reference_and_fast_agree_on_bounded_sample(monkeypatch):
  graphs = [
    _g6(nx.cycle_graph(5)),
    _g6(nx.cycle_graph(6)),
  ]

  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: graphs)
  monkeypatch.setattr(search_main, "passes_all_filters", lambda G: True)
  monkeypatch.setattr(search_main, "is_delta_critical", lambda G: True)

  reference = search_main.analyze_order(
    6,
    delta=2,
    workers=1,
    density_implementation="reference",
    limit_graphs=2,
  )
  fast = search_main.analyze_order(
    6,
    delta=2,
    workers=1,
    density_implementation="fast",
    limit_graphs=2,
  )

  keys = [
    "generated_biconnected",
    "processed_graphs",
    "pruned_by_filters",
    "class1_or_noncritical",
    "total_critical",
    "overfull_count",
    "survivor_count",
    "interrupted",
  ]
  assert {key: reference[key] for key in keys} == {key: fast[key] for key in keys}


def test_geng_stream_stops_after_limit_without_materializing_full_output(monkeypatch):
  class FakeProc:
    def __init__(self):
      self.stdout = io.StringIO(">A header line\nfirst\nsecond\nthird\nfourth\n")
      self.stderr = io.StringIO("")
      self.returncode = None
      self.terminated = False
      self.wait_calls = []

    def terminate(self):
      self.terminated = True
      self.returncode = -15

    def wait(self, timeout=None):
      self.wait_calls.append(timeout)
      if self.returncode is None:
        self.returncode = 0
      return self.returncode

    def kill(self):
      self.returncode = -9

  fake_proc = FakeProc()

  monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: fake_proc)

  result = search_main._geng_stream(13, 5, "/usr/bin/geng", min_degree=4, limit_graphs=2)

  assert result == ["first", "second"]
  assert fake_proc.terminated


def test_geng_stream_full_run_uses_tempfile_not_capture_output(monkeypatch):
  captured = {}

  def fake_run(cmd, stdout=None, stderr=None, text=None, timeout=None, check=False):
    assert stdout is not None
    assert stderr == subprocess.PIPE
    assert timeout == 7200
    captured["used_capture_output"] = False
    stdout.write(">header\nalpha\nbeta\n")
    stdout.flush()

    class Result:
      returncode = 0
      stderr = ""

    return Result()

  monkeypatch.setattr(subprocess, "run", fake_run)

  result = search_main._geng_stream(19, 3, "/usr/bin/geng", min_degree=2, limit_graphs=None)

  assert result == ["alpha", "beta"]
  assert captured["used_capture_output"] is False


def test_geng_stream_full_run_preserves_overall_timeout(monkeypatch):
  def fake_run(*args, **kwargs):
    raise subprocess.TimeoutExpired(args[0], kwargs.get("timeout", 7200))

  monkeypatch.setattr(subprocess, "run", fake_run)

  with pytest.raises(subprocess.TimeoutExpired):
    search_main._geng_stream(19, 3, "/usr/bin/geng", min_degree=2, limit_graphs=None)


def test_analyze_order_writes_partial_checkpoint_on_interrupt(monkeypatch, tmp_path):
  graphs = [_g6(nx.cycle_graph(5)), _g6(nx.cycle_graph(6)), _g6(nx.path_graph(4))]
  checkpoint_path = tmp_path / "order_19_delta_3.partial.json"

  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: graphs)

  results = iter([
    {"status": "survivor", "graph6": graphs[0], "edges": [], "degree_sequence": [2, 2, 2, 2, 2], "delta_max": 2, "delta_min": 2, "alpha": 2, "alpha_ratio": 0.4, "overfull_subsets": []},
    KeyboardInterrupt("stop now"),
  ])

  def fake_process(_args):
    result = next(results)
    if isinstance(result, BaseException):
      raise result
    return result

  monkeypatch.setattr(search_main, "_process_graph", fake_process)

  with pytest.raises(KeyboardInterrupt):
    search_main.analyze_order(
      19,
      delta=3,
      workers=1,
      checkpoint_path=checkpoint_path,
    )

  payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
  assert payload["order"] == 19
  assert payload["generated_biconnected"] == 3
  assert payload["processed_graphs"] == 1
  assert payload["total_critical"] == 1
  assert payload["survivor_count"] == 1
  assert payload["interrupted"] is True
  assert "stop now" in payload["interruption_reason"]


@pytest.mark.skipif(
  not hasattr(signal, "pthread_sigmask"),
  reason="POSIX signal masking is unavailable",
)
def test_defer_interrupts_finishes_counter_transaction_before_sigterm():
  previous_handler = signal.getsignal(signal.SIGTERM)
  state = []
  search_main._install_interrupt_handler()
  try:
    with pytest.raises(search_main.SearchInterrupted, match="Received signal"):
      with search_main._defer_interrupts():
        os.kill(os.getpid(), signal.SIGTERM)
        state.append("classification-applied")
  finally:
    signal.signal(signal.SIGTERM, previous_handler)

  assert state == ["classification-applied"]


def test_analyze_order_resumes_from_prefix_checkpoint(monkeypatch, tmp_path):
  graphs = [_g6(nx.cycle_graph(5)), _g6(nx.cycle_graph(6)), _g6(nx.path_graph(4))]
  checkpoint_path = tmp_path / "order_19_delta_3.partial.json"
  checkpoint_payload = {
    "order": 19,
    "delta_max": 3,
    "min_degree_bound": 2,
    "generated_biconnected": 3,
    "processed_graphs": 1,
    "pruned_by_filters": 0,
    "class1_or_noncritical": 0,
    "total_critical": 1,
    "overfull_count": 0,
    "survivor_count": 1,
    "survivors": [
      {
        "status": "survivor",
        "graph6": graphs[0],
        "edges": [],
        "degree_sequence": [2, 2, 2, 2, 2],
        "delta_max": 2,
        "delta_min": 2,
        "alpha": 2,
        "alpha_ratio": 0.4,
        "overfull_subsets": [],
      }
    ],
    "runtime_seconds": 1.0,
    "interrupted": True,
    "interruption_reason": "Received signal 15",
    "resume_safe": True,
    "resume_prefix_fingerprint": _fingerprint_prefix(graphs[:1]),
  }
  checkpoint_path.write_text(json.dumps(checkpoint_payload), encoding="utf-8")

  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: graphs)
  seen = []

  def fake_process(args):
    seen.append(args[0])
    if args[0] == graphs[1]:
      return {"status": "overfull"}
    if args[0] == graphs[2]:
      return {
        "status": "survivor",
        "graph6": graphs[2],
        "edges": [],
        "degree_sequence": [2, 1, 1, 0],
        "delta_max": 2,
        "delta_min": 0,
        "alpha": 3,
        "alpha_ratio": 0.75,
        "overfull_subsets": [],
      }
    raise AssertionError(f"Unexpected graph processed: {args[0]}")

  monkeypatch.setattr(search_main, "_process_graph", fake_process)

  result = search_main.analyze_order(
    19,
    delta=3,
    workers=1,
    checkpoint_path=checkpoint_path,
    resume_from_checkpoint=True,
  )

  assert seen == graphs[1:]
  assert result["generated_biconnected"] == 3
  assert result["processed_graphs"] == 3
  assert result["total_critical"] == 3
  assert result["overfull_count"] == 1
  assert result["survivor_count"] == 2
  assert [item["graph6"] for item in result["survivors"]] == [graphs[0], graphs[2]]
  assert result["interrupted"] is False


def test_resume_rejects_parallel_unsafe_checkpoint(tmp_path):
  checkpoint_path = tmp_path / "order_19_delta_3.partial.json"
  checkpoint_payload = {
    "order": 19,
    "delta_max": 3,
    "min_degree_bound": 2,
    "generated_biconnected": 10,
    "processed_graphs": 4,
    "pruned_by_filters": 0,
    "class1_or_noncritical": 0,
    "total_critical": 0,
    "overfull_count": 0,
    "survivor_count": 0,
    "survivors": [],
    "runtime_seconds": 1.0,
    "interrupted": True,
    "interruption_reason": "Received signal 15",
    "resume_safe": False,
  }
  checkpoint_path.write_text(json.dumps(checkpoint_payload), encoding="utf-8")

  with pytest.raises(ValueError, match="resume-safe"):
    search_main.analyze_order(
      19,
      delta=3,
      workers=1,
      checkpoint_path=checkpoint_path,
      resume_from_checkpoint=True,
    )


def test_resume_rejects_corrupt_checkpoint_file(monkeypatch, tmp_path):
  checkpoint_path = tmp_path / "order_19_delta_3.partial.json"
  checkpoint_path.write_text("{not valid json", encoding="utf-8")
  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: [])

  with pytest.raises(ValueError, match="Failed to load checkpoint"):
    search_main.analyze_order(
      19,
      delta=3,
      workers=1,
      checkpoint_path=checkpoint_path,
      resume_from_checkpoint=True,
    )


def test_resume_rejects_prefix_fingerprint_mismatch(monkeypatch, tmp_path):
  graphs = [_g6(nx.cycle_graph(5)), _g6(nx.cycle_graph(6)), _g6(nx.path_graph(4))]
  checkpoint_path = tmp_path / "order_19_delta_3.partial.json"
  checkpoint_payload = {
    "order": 19,
    "delta_max": 3,
    "min_degree_bound": 2,
    "generated_biconnected": 3,
    "processed_graphs": 1,
    "pruned_by_filters": 0,
    "class1_or_noncritical": 0,
    "total_critical": 1,
    "overfull_count": 0,
    "survivor_count": 1,
    "survivors": [],
    "runtime_seconds": 1.0,
    "interrupted": True,
    "interruption_reason": "Received signal 15",
    "resume_safe": True,
    "resume_prefix_fingerprint": _fingerprint_prefix([graphs[1]]),
  }
  checkpoint_path.write_text(json.dumps(checkpoint_payload), encoding="utf-8")
  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: graphs)

  with pytest.raises(ValueError, match="prefix fingerprint"):
    search_main.analyze_order(
      19,
      delta=3,
      workers=1,
      checkpoint_path=checkpoint_path,
      resume_from_checkpoint=True,
    )


def test_parallel_resume_caps_chunksize_to_keep_progress_responsive(monkeypatch, tmp_path):
  total_graphs = 2000001
  graphs = [f"g{i}" for i in range(total_graphs)]
  checkpoint_path = tmp_path / "order_19_delta_3.partial.json"
  checkpoint_payload = {
    "order": 19,
    "delta_max": 3,
    "min_degree_bound": 2,
    "generated_biconnected": len(graphs),
    "processed_graphs": 1,
    "pruned_by_filters": 0,
    "class1_or_noncritical": 0,
    "total_critical": 0,
    "overfull_count": 0,
    "survivor_count": 0,
    "survivors": [],
    "runtime_seconds": 1.0,
    "interrupted": True,
    "interruption_reason": "Received signal 15",
    "resume_safe": True,
    "resume_prefix_fingerprint": _fingerprint_prefix(graphs[:1]),
  }
  checkpoint_path.write_text(json.dumps(checkpoint_payload), encoding="utf-8")
  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: graphs)
  monkeypatch.setattr(search_main, "_process_graph", lambda args: None)

  seen = {}

  class FakePool:
    def __init__(self, workers):
      seen["workers"] = workers

    def imap(self, func, iterable, chunksize=1):
      seen["chunksize"] = chunksize
      for item in iterable:
        yield func(item)

    def close(self):
      seen["closed"] = True

    def join(self):
      seen["joined"] = True

    def terminate(self):
      seen["terminated"] = True

  monkeypatch.setattr(search_main.mp, "Pool", FakePool)

  result = search_main.analyze_order(
    19,
    delta=3,
    workers=14,
    checkpoint_path=checkpoint_path,
    resume_from_checkpoint=True,
  )

  assert result["processed_graphs"] == len(graphs)
  assert seen["workers"] == 14
  assert seen["chunksize"] <= 1000
  assert seen["closed"] is True
  assert seen["joined"] is True


def test_streaming_analyze_order_does_not_materialize_full_geng_output(monkeypatch):
  graphs = [_g6(nx.cycle_graph(5)), _g6(nx.cycle_graph(6)), _g6(nx.path_graph(4))]

  def fail_if_full_materializer_is_used(*_args, **_kwargs):
    raise AssertionError("streaming run must not call _geng_stream/full materializer")

  monkeypatch.setattr(search_main, "_geng_stream", fail_if_full_materializer_is_used)
  monkeypatch.setattr(search_main, "_iter_geng_stream", lambda *args, **kwargs: iter(graphs))
  monkeypatch.setattr(search_main, "_process_graph", lambda args: {"status": "pruned"})

  result = search_main.analyze_order(
    21,
    delta=3,
    workers=1,
    stream_geng=True,
  )

  assert result["generated_biconnected"] == 3
  assert result["processed_graphs"] == 3
  assert result["pruned_by_filters"] == 3
  assert result["streaming_geng"] is True
  assert result["generation_complete"] is True
  assert result["resume_safe"] is True
  assert result["resume_prefix_fingerprint"] == _fingerprint_prefix(graphs)


def test_streaming_analyze_order_writes_resume_safe_partial_on_interrupt(monkeypatch, tmp_path):
  graphs = [_g6(nx.cycle_graph(5)), _g6(nx.cycle_graph(6)), _g6(nx.path_graph(4))]
  checkpoint_path = tmp_path / "order_21_delta_3.partial.json"
  monkeypatch.setattr(search_main, "_iter_geng_stream", lambda *args, **kwargs: iter(graphs))

  results = iter([
    {"status": "pruned"},
    KeyboardInterrupt("stream stop"),
  ])

  def fake_process(_args):
    result = next(results)
    if isinstance(result, BaseException):
      raise result
    return result

  monkeypatch.setattr(search_main, "_process_graph", fake_process)

  with pytest.raises(KeyboardInterrupt):
    search_main.analyze_order(
      21,
      delta=3,
      workers=1,
      checkpoint_path=checkpoint_path,
      stream_geng=True,
    )

  payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
  assert payload["order"] == 21
  assert payload["generated_biconnected"] == 1
  assert payload["processed_graphs"] == 1
  assert payload["pruned_by_filters"] == 1
  assert payload["streaming_geng"] is True
  assert payload["generation_complete"] is False
  assert payload["resume_safe"] is True
  assert payload["resume_prefix_fingerprint"] == _fingerprint_prefix(graphs[:1])
  assert payload["interrupted"] is True
  assert "stream stop" in payload["interruption_reason"]


def test_streaming_resume_skips_validated_prefix_without_materializing(monkeypatch, tmp_path):
  graphs = [_g6(nx.cycle_graph(5)), _g6(nx.cycle_graph(6)), _g6(nx.path_graph(4))]
  checkpoint_path = tmp_path / "order_21_delta_3.partial.json"
  checkpoint_path.write_text(
    json.dumps(
      {
        "order": 21,
        "delta_max": 3,
        "min_degree_bound": 2,
        "generated_biconnected": 1,
        "processed_graphs": 1,
        "pruned_by_filters": 1,
        "class1_or_noncritical": 0,
        "total_critical": 0,
        "overfull_count": 0,
        "survivor_count": 0,
        "survivors": [],
        "runtime_seconds": 1.0,
        "interrupted": True,
        "interruption_reason": "Received signal 15",
        "resume_safe": True,
        "resume_prefix_fingerprint": _fingerprint_prefix(graphs[:1]),
        "streaming_geng": True,
        "generation_complete": False,
      }
    ),
    encoding="utf-8",
  )

  monkeypatch.setattr(search_main, "_geng_stream", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no materialization")))
  monkeypatch.setattr(search_main, "_iter_geng_stream", lambda *args, **kwargs: iter(graphs))
  seen = []

  def fake_process(args):
    seen.append(args[0])
    return {"status": "pruned"}

  monkeypatch.setattr(search_main, "_process_graph", fake_process)

  result = search_main.analyze_order(
    21,
    delta=3,
    workers=1,
    checkpoint_path=checkpoint_path,
    resume_from_checkpoint=True,
    stream_geng=True,
  )

  assert seen == graphs[1:]
  assert result["generated_biconnected"] == 3
  assert result["processed_graphs"] == 3
  assert result["pruned_by_filters"] == 3
  assert result["streaming_geng"] is True
  assert result["generation_complete"] is True


def test_streaming_parallel_exception_terminates_pool_and_closes_geng_iter(monkeypatch):
  class CloseAwareIter:
    def __init__(self):
      self.closed = False
      self.items = iter([_g6(nx.cycle_graph(5)), _g6(nx.cycle_graph(6))])

    def __iter__(self):
      return self

    def __next__(self):
      return next(self.items)

    def close(self):
      self.closed = True

  graph_iter = CloseAwareIter()
  monkeypatch.setattr(search_main, "_iter_geng_stream", lambda *args, **kwargs: graph_iter)
  seen = {}

  class FailingPool:
    def __init__(self, workers):
      seen["workers"] = workers

    def imap(self, _func, _iterable, chunksize=1):
      seen["chunksize"] = chunksize
      raise RuntimeError("worker failure")
      yield  # pragma: no cover

    def close(self):
      seen["closed"] = True

    def join(self):
      seen["joined"] = True

    def terminate(self):
      seen["terminated"] = True

  monkeypatch.setattr(search_main.mp, "Pool", FailingPool)

  with pytest.raises(RuntimeError, match="worker failure"):
    search_main.analyze_order(21, delta=3, workers=5, stream_geng=True)

  assert seen["terminated"] is True
  assert seen["joined"] is True
  assert graph_iter.closed is True
  assert "closed" not in seen


def test_iter_geng_stream_discards_stderr_to_avoid_pipe_deadlock(monkeypatch):
  class FakeProc:
    def __init__(self):
      self.stdout = io.StringIO(">header\nalpha\n")
      self.returncode = 0

    def wait(self, timeout=None):
      return self.returncode

    def poll(self):
      return self.returncode

  captured = {}

  def fake_popen(*args, **kwargs):
    captured["stderr"] = kwargs.get("stderr")
    return FakeProc()

  monkeypatch.setattr(subprocess, "Popen", fake_popen)

  assert list(search_main._iter_geng_stream(21, 3, "/usr/bin/geng")) == ["alpha"]
  assert captured["stderr"] == subprocess.DEVNULL
