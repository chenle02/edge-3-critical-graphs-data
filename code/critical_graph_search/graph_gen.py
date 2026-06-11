from __future__ import annotations

import shutil
import subprocess
from typing import Iterable, Iterator, Optional

import networkx as nx


def resolve_geng(explicit_path: Optional[str] = None) -> Optional[str]:
  if explicit_path and shutil.which(explicit_path):
    return explicit_path
  return shutil.which("geng") or ("/tmp/nauty2_8_9/geng" if shutil.which("/tmp/nauty2_8_9/geng") else None)


def generate_connected_bounded_degree_graphs(
  n: int,
  min_degree: int = 2,
  max_degree: int = 3,
  geng_path: Optional[str] = None,
  biconnected: bool = False,
) -> Iterator[nx.Graph]:
  gpath = resolve_geng(geng_path)
  if not gpath:
    raise RuntimeError(
      "geng/nauty is required for practical generation. Install nauty or pass --geng-path."
    )

  conn_flag = "-Cq" if biconnected else "-cq"
  cmd = [gpath, conn_flag, f"-d{min_degree}", f"-D{max_degree}", str(n)]
  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  assert proc.stdout is not None
  for line in proc.stdout:
    g6 = line.strip()
    if not g6 or g6.startswith(">"):
      continue
    G = nx.from_graph6_bytes(g6.encode("ascii"))
    if nx.is_connected(G):
      yield G
  _, err = proc.communicate()
  if proc.returncode != 0:
    raise RuntimeError(f"geng failed (code={proc.returncode}): {err}")
