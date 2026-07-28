# `native/` — C census filter

A standalone C reimplementation of the census inner loop, ~137× faster than the
Python pipeline (see `../docs/DECISIONS.md` **D-0002**). It is the fast **gate**;
the Python pipeline remains the reference and owns survivor-record construction.

This directory is the curated public mirror of the authoritative development
source. Internal `D-000N` labels below preserve engineering provenance; the
public Order-19 end-to-end receipt is
[`../../reports/order19_native_replay_20260728.md`](../../reports/order19_native_replay_20260728.md).

## What it does

`cfilter` reads graph6 lines (as emitted by `geng -Cq -d2 -D3 n`) on stdin and
writes the **survivor** graph6 lines on stdout: the nontrivial Δ=3 edge-critical
non-overfull graphs. Survivor definition (identical to `main.py:_process_graph`):

```
maxdeg == 3  AND  passes_all_filters  AND  is_delta_critical  AND  !has_overfull
```

Every branch in `cfilter.c` cites the Python source line it mirrors.

### Scale counters on stderr (D-0008)

At end of stream `cfilter` prints ONE line to **stderr** recording the census
scale (stdout stays pure survivor graph6, so the Python pipeline is unaffected):

```
CFILTER_STATS read=<N> maxdeg3=<N> val_pass=<N> filt_pass=<N> critical=<N> survivors=<N>
```

`read` is the raw candidate population geng produced (the number that conveys the
scale of the search). `main.py` captures and stores it as `generated_biconnected`.
Before D-0008 the streaming path recorded only the survivor count here, so the
raw generation count for C-filter orders (24+) was lost. Example (order 15):
`read=165993 ... survivors=94`.

### Vizing's Adjacency Lemma pre-filter (D-0006)

`cfilter` additionally applies a **necessary-only** Vizing-Adjacency-Lemma (VAL)
pre-filter (`val_rejects`) right after the `maxdeg==3` gate, **before** the
expensive `is_delta_critical` edge-colouring DFS. For Δ=3 the classical edge-VAL
collapses to a cheap vertex condition: **every vertex must have ≥2 neighbours of
degree 3, and 2·n₂ ≤ n₃** (n₂/n₃ = counts of degree-2/3 vertices). VAL is a
necessary condition for Δ-criticality, so it **never changes the survivor set** —
verified: it rejects **0 / 782,186** real order-23 survivors (Python + C), and the
canonical survivor sets for orders 13/15/17 are unchanged. It prunes ~87–100% of
geng candidates, so the criticality DFS runs on a small fraction of the input.
This is why the C filter can carry a filter the Python reference (`pyref.py`) does
not, yet still pass the bit-equality gate.

## Build

```bash
cc -std=gnu11 -O3 -Wall -Wextra -o cfilter cfilter.c
```

> **Do NOT add `-march=native`** and use a **modern gcc** (≥ 5; on Easley
> `module load gcc/13.3.0`). Easley's default `cc` is gcc 4.8.5 (2015), and
> `gcc 4.8.5 -O3 -march=native` intermittently SIGSEGVs on some of the cluster's
> heterogeneous CPUs (killed ~60/400 order-24 tasks; see `../docs/DECISIONS.md`
> **D-0005**). The C code is clean (full failing slice passes ASan+UBSan under
> gcc 16); the ~137× speedup is algorithmic, so plain `-O3` is both safe and fast.

## Run

```bash
# whole order
geng -Cq -d2 -D3 17 | ./cfilter

# Slurm array task (nauty modular split res/mod)
geng -Cq -d2 -D3 24 5/64 | ./cfilter
```

## Validate (mandatory before any production use)

```bash
./validate.sh
```

Rebuilds, runs orders 13/15/17, and checks the C survivor set equals the Python
reference (`pyref.py`) — comparing nauty **canonical** forms via `labelg`, the
true graph-identity check. Known counts: 13→14, 15→94, 17→774. Exit 0 iff all
match. This is the D-0002 regression gate; run it after any edit to `cfilter.c`.

## Files

| File | Purpose |
|---|---|
| `cfilter.c` | the filter (graph6 decode + pruning + criticality + overfull) |
| `pyref.py` | Python reference filter (bit-equality ground truth) |
| `validate.sh` | bit-equality regression gate (orders 13/15/17) |

## Labeling caveat

`cfilter` emits geng's canonical graph6; the Python pipeline stores an
`nx`-round-tripped graph6 (different labeling of the SAME graph). The survivor
SETS are identical up to isomorphism (proven by `labelg`). The census merge relies
on geng's disjoint modular split, not graph6-string dedup, so this is safe. To get
the Python's exact graph6 strings or survivor metadata (edges, α), feed the
C-filter survivor lines back through the Python record-builder.

## Performance

Single-thread, order-15 stream (165,993 graphs): C = 1.45 s vs Python = 198.0 s
(**≈137×**), peak RSS 1.4 MB. Parallelism is provided by the Slurm array + geng
`res/mod`; each task runs one single-thread `cfilter`.
