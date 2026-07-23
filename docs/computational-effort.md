# Computational effort

This page records the computational cost of the completed Order 21, Order 22,
and Order 23 censuses. The figures come from sanitized result metadata and
top-level Slurm accounting retained on the Auburn University Easley Cluster.

## Campaign summary

| Order | Status | Slices | Processed graphs | Survivors | Slurm attempts | Cumulative Slurm wall | Allocated compute | Calendar span |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 21 | Complete | 16/16 | 1,068,435,908 | 70,530 | 16 | 7d 18:45:54 | **8,964.720 core-hours** | 23:52:47 |
| 22 | Complete | 16/16 | 5,022,269,988 | 1 | 16 | 1d 17:18:49 | **1,983.053 core-hours** | 5:20:59 |
| 23 | Complete | 64/64 | 24,086,917,749 | 782,186 | 106 | 939d 08:50:09 | **723,371.786 core-hours** | 54d 11:37:15 |

Order 21 ran from 2026-05-07 20:37:06 to 2026-05-08 20:29:53, and
Order 22 ran from 2026-05-08 21:43:03 to 2026-05-09 03:04:02. These Slurm
timestamps use `America/Chicago`. Both completed campaigns used 16 successful
48-CPU tasks, with no retries recorded.

The exact Order 21 accounting supersedes the earlier planning estimate of
approximately 18,400 core-hours. That estimate assumed all 16 allocations ran
for the entire approximately 24-hour calendar span. Slurm accounting instead
sums the actual allocation durations and gives 8,964.720 core-hours.

## Detailed reports and machine-readable telemetry

| Order | Detailed report | Canonical snapshot | Flat telemetry |
|---:|:---|:---|:---|
| 21 | [Markdown](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order21_computational_effort_20260722.md) | [JSON](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order21_computational_effort_20260722.json) | [TSV](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order21_computational_effort_20260722.tsv) |
| 22 | [Markdown](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order22_computational_effort_20260722.md) | [JSON](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order22_computational_effort_20260722.json) | [TSV](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order22_computational_effort_20260722.tsv) |
| 23 | [Markdown](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order23_computational_effort_20260723.md) | [JSON](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order23_computational_effort_20260723.json) | [TSV](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order23_computational_effort_20260723.tsv) |

The detailed reports provide per-slice dates, counters, attempt states, wall
times, and core-hours. The JSON snapshots are the canonical sanitized records;
the Markdown and TSV files are deterministic renderings.

## Definitions and caveats

- **Cumulative Slurm wall time** is the sum of `ElapsedRaw` over top-level
  attempts. It is not the elapsed calendar duration of a parallel campaign.
- **Allocated compute** is the sum of `ElapsedRaw × AllocCPUS / 3600`, so it
  reflects actual allocation durations, retries, and mixed CPU allocations.
- **Calendar span** is the interval from the earliest task start to the latest
  task end. Parallel task execution makes it much smaller than cumulative wall
  time.
- Order 23 completed on 2026-07-23: all 64 canonical-prefix slices reached a
  final result and were merged into a single census file (782,186 nontrivial
  survivors). The Order 23 figures above are final, not provisional.
- The public snapshots contain no usernames, account names, source paths,
  nodes, commands, or raw log streams.

## Acknowledgment

This work was completed in part with resources provided by the Auburn University Easley Cluster.
