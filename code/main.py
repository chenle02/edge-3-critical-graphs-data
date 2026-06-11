from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import signal
import sys
import time
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import networkx as nx

from critical_graph_search.criticality import is_delta_critical
from critical_graph_search.density_filter import has_overfull_subgraph
from critical_graph_search.edge_coloring import is_class2
from critical_graph_search.pruning import passes_all_filters


class SearchInterrupted(KeyboardInterrupt):
  """Raised when a long search is interrupted but should checkpoint first."""


def _install_interrupt_handler() -> None:
  def _handle_signal(signum, _frame):
    raise SearchInterrupted(f"Received signal {signum}")

  signal.signal(signal.SIGTERM, _handle_signal)


def independence_number(G: nx.Graph) -> int:
  nodes = list(G.nodes())
  n = len(nodes)
  for r in range(n, -1, -1):
    for subset in combinations(nodes, r):
      H = G.subgraph(subset)
      if H.number_of_edges() == 0:
        return r
  return 0


def _process_graph(args: Tuple[str, int, str]) -> Optional[Dict]:
  g6_str, delta, density_implementation = args
  try:
    G = nx.from_graph6_bytes(g6_str.encode("ascii"))
  except Exception:
    return None

  if max(d for _, d in G.degree()) != delta:
    return None

  if not passes_all_filters(G):
    return {"status": "pruned"}

  if not is_delta_critical(G):
    return {"status": "class1"}

  has_overfull, _ = has_overfull_subgraph(
    G,
    delta=delta,
    stop_on_first=True,
    implementation=density_implementation,
  )
  if has_overfull:
    return {"status": "overfull"}

  n = G.number_of_nodes()
  alpha = independence_number(G)
  degree_seq = sorted((int(d) for _, d in G.degree()), reverse=True)
  return {
    "status": "survivor",
    "graph6": g6_str,
    "edges": sorted((int(u), int(v)) for u, v in G.edges()),
    "degree_sequence": degree_seq,
    "delta_max": delta,
    "delta_min": degree_seq[-1],
    "alpha": alpha,
    "alpha_ratio": alpha / n,
    "overfull_subsets": [],
  }


def _geng_command(
  n: int,
  delta: int,
  geng_path: Optional[str],
  min_degree: int = 2,
  mod_split: Optional[Tuple[int, int]] = None,
) -> List[str]:
  import shutil

  gpath = geng_path or shutil.which("geng")
  if not gpath:
    raise RuntimeError("geng not found")
  cmd = [gpath, "-Cq", f"-d{min_degree}", f"-D{delta}", str(n)]
  if mod_split is not None:
    m, total = mod_split
    if total < 1:
      raise ValueError(f"--geng-mod N must be >= 1, got N={total}")
    if not (0 <= m < total):
      raise ValueError(f"--geng-mod requires 0 <= m < N, got m={m} N={total}")
    cmd.append(f"{m}/{total}")
  return cmd


def _geng_stream(
  n: int,
  delta: int,
  geng_path: Optional[str],
  min_degree: int = 2,
  limit_graphs: int | None = None,
  mod_split: Optional[Tuple[int, int]] = None,
) -> List[str]:
  import subprocess
  import tempfile

  cmd = _geng_command(n, delta, geng_path, min_degree=min_degree, mod_split=mod_split)

  if limit_graphs is None:
    with tempfile.TemporaryFile(mode="w+") as tmp_stdout:
      proc = subprocess.run(
        cmd,
        stdout=tmp_stdout,
        stderr=subprocess.PIPE,
        text=True,
        timeout=7200,
        check=False,
      )
      if proc.returncode != 0:
        raise RuntimeError(f"geng failed: {proc.stderr}")
      tmp_stdout.seek(0)
      return [
        line.strip()
        for line in tmp_stdout
        if line.strip() and not line.startswith(">")
      ]

  proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
  )
  assert proc.stdout is not None
  lines: List[str] = []
  try:
    for raw_line in proc.stdout:
      line = raw_line.strip()
      if not line or line.startswith(">"):
        continue
      lines.append(line)
      if limit_graphs is not None and len(lines) >= limit_graphs:
        proc.terminate()
        break
    proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
    if proc.returncode is None:
      proc.kill()
      proc.wait(timeout=5)
    raise

  if proc.returncode not in (0, -15):
    stderr = proc.stderr.read() if proc.stderr is not None else ""
    raise RuntimeError(f"geng failed: {stderr}")

  return lines


def _iter_geng_stream(
  n: int,
  delta: int,
  geng_path: Optional[str],
  min_degree: int = 2,
  mod_split: Optional[Tuple[int, int]] = None,
) -> Iterator[str]:
  """Yield geng graph6 lines without materializing the full output."""
  import subprocess

  cmd = _geng_command(n, delta, geng_path, min_degree=min_degree, mod_split=mod_split)
  proc = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
  )
  assert proc.stdout is not None
  try:
    for raw_line in proc.stdout:
      line = raw_line.strip()
      if line and not line.startswith(">"):
        yield line
    returncode = proc.wait()
    if returncode != 0:
      raise RuntimeError(f"geng failed with return code {returncode}")
  except BaseException:
    if proc.poll() is None:
      proc.terminate()
      try:
        proc.wait(timeout=5)
      except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    raise


def _build_record(
  n: int,
  delta: int,
  min_degree: int,
  generated_biconnected: int,
  pruned_count: int,
  class1_count: int,
  total_critical: int,
  overfull_count: int,
  survivors: List[Dict],
  t0: float,
  processed_graphs: int | None = None,
  interrupted: bool = False,
  interruption_reason: str | None = None,
) -> Dict:
  return {
    "order": n,
    "delta_max": delta,
    "min_degree_bound": min_degree,
    "generated_biconnected": generated_biconnected,
    "processed_graphs": generated_biconnected if processed_graphs is None else processed_graphs,
    "pruned_by_filters": pruned_count,
    "class1_or_noncritical": class1_count,
    "total_critical": total_critical,
    "overfull_count": overfull_count,
    "survivor_count": len(survivors),
    "survivors": survivors,
    "runtime_seconds": round(time.time() - t0, 3),
    "interrupted": interrupted,
    "interruption_reason": interruption_reason,
  }


def _write_json(path: Path, payload: Dict) -> None:
  import os

  path.parent.mkdir(parents=True, exist_ok=True)
  tmp_path = path.with_name(f".{path.name}.tmp.{os.getpid()}")
  tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
  tmp_path.replace(path)


def _load_checkpoint(path: Path) -> Dict:
  try:
    return json.loads(path.read_text(encoding="utf-8"))
  except (OSError, json.JSONDecodeError) as exc:
    raise ValueError(f"Failed to load checkpoint {path}: {exc}") from exc


def _update_prefix_fingerprint(current: str, g6: str) -> str:
  h = hashlib.sha256()
  h.update(bytes.fromhex(current))
  h.update(b"\0")
  h.update(g6.encode("ascii"))
  return h.hexdigest()


def _process_graph_with_g6(args: Tuple[str, int, str]) -> Tuple[str, Optional[Dict]]:
  return args[0], _process_graph(args)


def _apply_process_result(
  result: Optional[Dict],
  counts: Dict[str, int],
  survivors: List[Dict],
) -> None:
  if result is None:
    return
  status = result.get("status")
  if status == "pruned":
    counts["pruned_count"] += 1
  elif status == "class1":
    counts["class1_count"] += 1
  elif status == "overfull":
    counts["total_critical"] += 1
    counts["overfull_count"] += 1
  elif status == "survivor":
    counts["total_critical"] += 1
    survivors.append(result)


def _analyze_order_streaming(
  n: int,
  delta: int,
  geng_path: str | None = None,
  workers: int = 0,
  min_degree: int = 2,
  density_implementation: str = "fast",
  checkpoint_path: Path | None = None,
  resume_from_checkpoint: bool = False,
  mod_split: Optional[Tuple[int, int]] = None,
) -> Dict:
  t0 = time.time()
  checkpoint_payload: Dict | None = None
  done = 0
  prefix_fingerprint = "00" * 32
  counts = {
    "pruned_count": 0,
    "class1_count": 0,
    "total_critical": 0,
    "overfull_count": 0,
  }
  survivors: List[Dict] = []

  if resume_from_checkpoint:
    if checkpoint_path is None or not checkpoint_path.exists():
      raise ValueError("Cannot resume without an existing checkpoint file")
    checkpoint_payload = _load_checkpoint(checkpoint_path)
    if checkpoint_payload.get("order") != n or checkpoint_payload.get("delta_max") != delta:
      raise ValueError("Checkpoint does not match requested order/delta")
    if checkpoint_payload.get("min_degree_bound", min_degree) != min_degree:
      raise ValueError("Checkpoint min-degree bound does not match requested run")
    if not checkpoint_payload.get("resume_safe", False):
      raise ValueError("Checkpoint is not marked resume-safe; restart from scratch instead")
    done = int(checkpoint_payload.get("processed_graphs", 0))
    counts["pruned_count"] = int(checkpoint_payload.get("pruned_by_filters", 0))
    counts["class1_count"] = int(checkpoint_payload.get("class1_or_noncritical", 0))
    counts["total_critical"] = int(checkpoint_payload.get("total_critical", 0))
    counts["overfull_count"] = int(checkpoint_payload.get("overfull_count", 0))
    survivors = list(checkpoint_payload.get("survivors", []))

  mod_label = ""
  if mod_split is not None:
    mod_label = f", part {mod_split[0]}/{mod_split[1]}"
  print(
    f"  Streaming graphs from geng (n={n}, Δ={delta}, δ≥{min_degree}, 2-connected{mod_label})...",
    file=sys.stderr,
  )
  graph_iter = iter(_iter_geng_stream(n, delta, geng_path, min_degree=min_degree, mod_split=mod_split))

  if resume_from_checkpoint:
    assert checkpoint_payload is not None
    expected_fingerprint = checkpoint_payload.get("resume_prefix_fingerprint")
    if not expected_fingerprint:
      raise ValueError("Checkpoint is missing resume prefix fingerprint")
    for skipped in range(done):
      try:
        g6 = next(graph_iter)
      except StopIteration as exc:
        raise ValueError("Checkpoint processed_graphs exceeds current geng stream") from exc
      prefix_fingerprint = _update_prefix_fingerprint(prefix_fingerprint, g6)
    if prefix_fingerprint != expected_fingerprint:
      raise ValueError("Checkpoint prefix fingerprint does not match current geng stream")
    print(f"  Resuming from checkpoint {checkpoint_path} at prefix {done}", file=sys.stderr)

  if workers <= 0:
    workers = max(1, mp.cpu_count() - 2)

  def checkpoint(reason: str | None = None, generation_complete: bool = False) -> Dict:
    record = _build_record(
      n=n,
      delta=delta,
      min_degree=min_degree,
      generated_biconnected=done,
      processed_graphs=done,
      pruned_count=counts["pruned_count"],
      class1_count=counts["class1_count"],
      total_critical=counts["total_critical"],
      overfull_count=counts["overfull_count"],
      survivors=survivors,
      t0=t0,
      interrupted=reason is not None,
      interruption_reason=reason,
    )
    record["resume_safe"] = True
    record["resume_prefix_fingerprint"] = prefix_fingerprint
    record["streaming_geng"] = True
    record["generation_complete"] = generation_complete
    if mod_split is not None:
      record["mod_split"] = {"m": mod_split[0], "N": mod_split[1]}
    if checkpoint_path is not None:
      _write_json(checkpoint_path, record)
    return record

  def record_processed(g6: str, result: Optional[Dict]) -> None:
    nonlocal done, prefix_fingerprint
    done += 1
    prefix_fingerprint = _update_prefix_fingerprint(prefix_fingerprint, g6)
    _apply_process_result(result, counts, survivors)
    if done % 100000 == 0:
      elapsed = time.time() - t0
      print(
        f"  [{done}/? streaming] critical={counts['total_critical']}, "
        f"survivors={len(survivors)}, elapsed={elapsed:.1f}s",
        file=sys.stderr,
      )
      checkpoint()

  if workers > 1:
    print(f"  Processing streaming graphs with {workers} workers...", file=sys.stderr)
    task_iter = ((g6, delta, density_implementation) for g6 in graph_iter)
    pool = mp.Pool(workers)
    try:
      for g6, result in pool.imap(_process_graph_with_g6, task_iter, chunksize=1000):
        record_processed(g6, result)
      pool.close()
      pool.join()
    except (KeyboardInterrupt, SearchInterrupted) as exc:
      pool.terminate()
      pool.join()
      checkpoint(str(exc) or exc.__class__.__name__, generation_complete=False)
      if hasattr(graph_iter, "close"):
        graph_iter.close()
      raise
    except BaseException:
      pool.terminate()
      pool.join()
      if hasattr(graph_iter, "close"):
        graph_iter.close()
      raise
  else:
    try:
      for g6 in graph_iter:
        result = _process_graph((g6, delta, density_implementation))
        record_processed(g6, result)
    except (KeyboardInterrupt, SearchInterrupted) as exc:
      checkpoint(str(exc) or exc.__class__.__name__, generation_complete=False)
      if hasattr(graph_iter, "close"):
        graph_iter.close()
      raise

  return checkpoint(generation_complete=True)


def analyze_order(
  n: int,
  delta: int,
  geng_path: str | None = None,
  workers: int = 0,
  min_degree: int = 2,
  density_implementation: str = "fast",
  limit_graphs: int | None = None,
  checkpoint_path: Path | None = None,
  resume_from_checkpoint: bool = False,
  stream_geng: bool = False,
  mod_split: Optional[Tuple[int, int]] = None,
) -> Dict:
  if mod_split is not None and not stream_geng:
    raise ValueError("--geng-mod requires --stream-geng (modular splits are only supported in streaming mode)")
  if stream_geng and limit_graphs is None:
    return _analyze_order_streaming(
      n,
      delta=delta,
      geng_path=geng_path,
      workers=workers,
      min_degree=min_degree,
      density_implementation=density_implementation,
      checkpoint_path=checkpoint_path,
      resume_from_checkpoint=resume_from_checkpoint,
      mod_split=mod_split,
    )

  t0 = time.time()
  checkpoint_payload: Dict | None = None

  if resume_from_checkpoint:
    if checkpoint_path is None or not checkpoint_path.exists():
      raise ValueError("Cannot resume without an existing checkpoint file")
    checkpoint_payload = _load_checkpoint(checkpoint_path)
    if checkpoint_payload.get("order") != n or checkpoint_payload.get("delta_max") != delta:
      raise ValueError("Checkpoint does not match requested order/delta")
    if checkpoint_payload.get("min_degree_bound", min_degree) != min_degree:
      raise ValueError("Checkpoint min-degree bound does not match requested run")
    if not checkpoint_payload.get("resume_safe", False):
      raise ValueError("Checkpoint is not marked resume-safe; restart from scratch instead")

  print(
    f"  Generating graphs with geng (n={n}, Δ={delta}, δ≥{min_degree}, 2-connected)...",
    file=sys.stderr,
  )
  all_g6 = _geng_stream(
    n,
    delta,
    geng_path,
    min_degree=min_degree,
    limit_graphs=limit_graphs,
  )
  if limit_graphs is not None:
    all_g6 = all_g6[:limit_graphs]
    print(f"  Limiting analysis to first {len(all_g6)} generated graphs", file=sys.stderr)
  gen_time = time.time() - t0
  print(f"  geng produced {len(all_g6)} graphs in {gen_time:.1f}s", file=sys.stderr)

  if workers <= 0:
    workers = max(1, mp.cpu_count() - 2)

  pruned_count = 0
  class1_count = 0
  total_critical = 0
  overfull_count = 0
  survivors: List[Dict] = []
  done = 0
  prefix_fingerprint = "00" * 32

  if resume_from_checkpoint:
    assert checkpoint_payload is not None
    done = int(checkpoint_payload.get("processed_graphs", 0))
    pruned_count = int(checkpoint_payload.get("pruned_by_filters", 0))
    class1_count = int(checkpoint_payload.get("class1_or_noncritical", 0))
    total_critical = int(checkpoint_payload.get("total_critical", 0))
    overfull_count = int(checkpoint_payload.get("overfull_count", 0))
    survivors = list(checkpoint_payload.get("survivors", []))
    generated_before = int(checkpoint_payload.get("generated_biconnected", len(all_g6)))
    if generated_before != len(all_g6):
      raise ValueError("Checkpoint generated graph count does not match current geng stream")
    if done > len(all_g6):
      raise ValueError("Checkpoint processed_graphs exceeds generated graph count")
    expected_fingerprint = checkpoint_payload.get("resume_prefix_fingerprint")
    if not expected_fingerprint:
      raise ValueError("Checkpoint is missing resume prefix fingerprint")
    prefix_fingerprint = "00" * 32
    for g6 in all_g6[:done]:
      prefix_fingerprint = _update_prefix_fingerprint(prefix_fingerprint, g6)
    if prefix_fingerprint != expected_fingerprint:
      raise ValueError("Checkpoint prefix fingerprint does not match current geng stream")
    print(f"  Resuming from checkpoint {checkpoint_path} at prefix {done}/{len(all_g6)}", file=sys.stderr)

  def checkpoint(reason: str | None = None) -> Dict:
    record = _build_record(
      n=n,
      delta=delta,
      min_degree=min_degree,
      generated_biconnected=len(all_g6),
      processed_graphs=done,
      pruned_count=pruned_count,
      class1_count=class1_count,
      total_critical=total_critical,
      overfull_count=overfull_count,
      survivors=survivors,
      t0=t0,
      interrupted=reason is not None,
      interruption_reason=reason,
    )
    record["resume_safe"] = True
    record["resume_prefix_fingerprint"] = prefix_fingerprint
    if checkpoint_path is not None:
      _write_json(checkpoint_path, record)
    return record

  remaining_g6 = all_g6[done:]
  task_args = [(g6, delta, density_implementation) for g6 in remaining_g6]

  use_parallel = len(all_g6) > 5000 and workers > 1

  if use_parallel:
    print(f"  Processing {len(remaining_g6)} remaining graphs with {workers} workers...", file=sys.stderr)
    chunksize = min(1000, max(100, len(remaining_g6) // (workers * 10)))
    pool = mp.Pool(workers)
    try:
      for g6, result in zip(remaining_g6, pool.imap(_process_graph, task_args, chunksize=chunksize)):
        done += 1
        prefix_fingerprint = _update_prefix_fingerprint(prefix_fingerprint, g6)
        if done % 100000 == 0:
          elapsed = time.time() - t0
          print(
            f"  [{done}/{len(all_g6)}] critical={total_critical}, "
            f"survivors={len(survivors)}, elapsed={elapsed:.1f}s",
            file=sys.stderr,
          )
          checkpoint()
        if result is None:
          continue
        status = result.get("status")
        if status == "pruned":
          pruned_count += 1
        elif status == "class1":
          class1_count += 1
        elif status == "overfull":
          total_critical += 1
          overfull_count += 1
        elif status == "survivor":
          total_critical += 1
          survivors.append(result)
      pool.close()
      pool.join()
    except (KeyboardInterrupt, SearchInterrupted) as exc:
      pool.terminate()
      pool.join()
      checkpoint(str(exc) or exc.__class__.__name__)
      raise
  else:
    try:
      for g6, delta_arg, density_impl in task_args:
        result = _process_graph((g6, delta_arg, density_impl))
        done += 1
        prefix_fingerprint = _update_prefix_fingerprint(prefix_fingerprint, g6)
        if result is None:
          continue
        status = result.get("status")
        if status == "pruned":
          pruned_count += 1
        elif status == "class1":
          class1_count += 1
        elif status == "overfull":
          total_critical += 1
          overfull_count += 1
        elif status == "survivor":
          total_critical += 1
          survivors.append(result)
    except (KeyboardInterrupt, SearchInterrupted) as exc:
      checkpoint(str(exc) or exc.__class__.__name__)
      raise

  return checkpoint()


def write_summary(results_dir: Path, per_order: List[Dict]) -> None:
  lines = [
    "# Critical Graph Search Summary",
    "",
    "| n | Δ | Generated (2-conn) | Pruned | Critical | Overfull | Survivors | Max α/n | Runtime (s) |",
    "|---|---|---:|---:|---:|---:|---:|---:|---:|",
  ]
  for rec in per_order:
    max_alpha_ratio = max((s["alpha_ratio"] for s in rec["survivors"]), default=0.0)
    lines.append(
      f"| {rec['order']} | {rec['delta_max']} "
      f"| {rec['generated_biconnected']} | {rec['pruned_by_filters']} "
      f"| {rec['total_critical']} | {rec['overfull_count']} "
      f"| {rec['survivor_count']} | {max_alpha_ratio:.4f} "
      f"| {rec['runtime_seconds']:.1f} |"
    )
  (results_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
  _install_interrupt_handler()
  parser = argparse.ArgumentParser(
    description="Edge-chromatic critical graph search with overfull filtering"
  )
  parser.add_argument("--orders", nargs="+", type=int, default=[13])
  parser.add_argument("--delta", type=int, default=3)
  parser.add_argument("--workers", type=int, default=0)
  parser.add_argument("--min-degree", type=int, default=2)
  parser.add_argument("--geng-path", default=None)
  parser.add_argument("--resume", action="store_true")
  parser.add_argument(
    "--stream-geng",
    action="store_true",
    help="stream geng output directly instead of materializing all graph6 lines in memory",
  )
  parser.add_argument(
    "--geng-mod",
    default=None,
    metavar="m/N",
    help="modular geng splitting via nauty's `geng <n> m/N` syntax — process only the m-th of N canonical-prefix classes. Use for Slurm job arrays. Requires --stream-geng. Each part writes its own results/checkpoint file.",
  )
  parser.add_argument(
    "--results-dir",
    default=None,
    help="absolute path to write results JSON + per-order checkpoints (default: ./results, relative to cwd). Set this when running under sbatch on Easley to avoid the cwd-vs-watch-script path mismatch documented in scripts/easley/PLAN-orders-22-24.md.",
  )
  args = parser.parse_args()

  mod_split: Optional[Tuple[int, int]] = None
  mod_filename_suffix = ""
  if args.geng_mod is not None:
    parts = args.geng_mod.split("/")
    if len(parts) != 2:
      parser.error(f"--geng-mod must be 'm/N', got {args.geng_mod!r}")
    try:
      m_value, total_value = int(parts[0]), int(parts[1])
    except ValueError:
      parser.error(f"--geng-mod m and N must be integers, got {args.geng_mod!r}")
    if total_value < 1 or not (0 <= m_value < total_value):
      parser.error(f"--geng-mod requires 0 <= m < N >= 1, got {args.geng_mod!r}")
    mod_split = (m_value, total_value)
    width = max(2, len(str(total_value - 1)))
    mod_filename_suffix = f"_part{m_value:0{width}d}of{total_value}"

  results_dir = Path(args.results_dir) if args.results_dir else Path("results")
  results_dir.mkdir(parents=True, exist_ok=True)

  all_results: List[Dict] = []
  for n in args.orders:
    mod_banner = f", part {mod_split[0]}/{mod_split[1]}" if mod_split else ""
    print(f"=== Scanning n={n}, Δ={args.delta}, δ≥{args.min_degree}{mod_banner} ===")
    suffix = f"_mindeg{args.min_degree}" if args.min_degree > 2 else ""
    outfile = results_dir / f"order_{n}_delta_{args.delta}{suffix}{mod_filename_suffix}.json"
    checkpoint_path = results_dir / f"order_{n}_delta_{args.delta}{suffix}{mod_filename_suffix}.partial.json"
    try:
      rec = analyze_order(
        n,
        delta=args.delta,
        geng_path=args.geng_path,
        workers=args.workers,
        min_degree=args.min_degree,
        checkpoint_path=checkpoint_path,
        resume_from_checkpoint=args.resume,
        stream_geng=args.stream_geng,
        mod_split=mod_split,
      )
    except (KeyboardInterrupt, SearchInterrupted) as exc:
      print(f"Interrupted while scanning n={n}, Δ={args.delta}: {exc}", file=sys.stderr)
      print(f"Partial results written to {checkpoint_path}", file=sys.stderr)
      raise
    all_results.append(rec)
    _write_json(outfile, rec)
    if checkpoint_path.exists():
      checkpoint_path.unlink()
    print(
      f"n={n}, Δ={args.delta}: generated={rec['generated_biconnected']}, "
      f"pruned={rec['pruned_by_filters']}, "
      f"critical={rec['total_critical']}, overfull={rec['overfull_count']}, "
      f"survivors={rec['survivor_count']}, "
      f"time={rec['runtime_seconds']:.1f}s"
    )

  write_summary(results_dir, all_results)
  print("Summary written to results/summary.md")


if __name__ == "__main__":
  main()
