# Computational effort

This page records the computational cost of the completed Order 21 through
Order 24 censuses and a provisional snapshot of the ongoing Order-25 census. The figures come from sanitized result metadata and
top-level Slurm accounting retained on the Auburn University Easley Cluster.

## Campaign summary

| Order | Status | Slices | Processed graphs | Survivors | Slurm attempts | Cumulative Slurm wall | Allocated compute | Calendar span |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| 21 | Complete | 16/16 | 1,068,435,908 | 70,530 | 16 | 7d 18:45:54 | **8,964.720 core-hours** | 23:52:47 |
| 22 | Complete | 16/16 | 5,022,269,988 | 1 | 16 | 1d 17:18:49 | **1,983.053 core-hours** | 5:20:59 |
| 23 | Complete | 64/64 | 24,086,917,749 | 782,186 | 106 | 939d 08:50:09 | **723,371.786 core-hours** | 54d 11:37:15 |
| 24 | Complete | 1024/1024 | not retained by streaming filter | 9 | — | — | **≈1,230 core-hours** | 13.3 h |
| 25 | **Running (provisional, 2026-10-19T03:21:37Z)** | 2994/4096 | 410,816,980,184 (completed slices) | 3,590,186 (completed slices) | 6,882 | 95832d 22:58:50 | **2,299,990.981 core-hours** (to date) | running since 2026-07-25 |

Order 21 ran from 2026-05-07 20:37:06 to 2026-05-08 20:29:53, and
Order 22 ran from 2026-05-08 21:43:03 to 2026-05-09 03:04:02. These Slurm
timestamps use `America/Chicago`. Both completed campaigns used 16 successful
48-CPU tasks, with no retries recorded.

The Order-24 native filter wrote only survivors to its output stream. The
archived merged record therefore contains all nine survivors but not the exact
number of raw `geng` candidates; the pre-flight estimate was approximately
3.4×10¹¹. All 1024 final slices completed, and the quoted cost and calendar
span come from the completed campaign summary.

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
| 25 (provisional, 2026-10-18T15:06Z) | [Markdown](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order25_computational_effort_20261018.md) | [JSON](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order25_computational_effort_20261018.json) | [TSV](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order25_computational_effort_20261018.tsv) |
| 25 (provisional, 2026-10-19T03:21Z, latest) | [Markdown](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order25_computational_effort_20261019.md) | [JSON](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order25_computational_effort_20261019.json) | [TSV](https://github.com/chenle02/edge-3-critical-graphs-data/blob/master/reports/order25_computational_effort_20261019.tsv) |

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
- Order 24 completed with 1024 final slices and nine nontrivial survivors.
  Because raw-stream counters were not retained, the page does not promote the
  candidate-population estimate to an exact count.
- Order 25 is still running. Its snapshots are provisional and not a census
  result. In the latest one (2026-10-19T03:21:37Z), graph counters come from
  the native C-filter's `cfilter_stats` and cover the 2,994 completed slices
  only (partial checkpoints carry no native counters, so they are withheld),
  while the Slurm figures cover every attempt to date, including the 1,101 live
  slices. One slice finished during collection and is recorded as partial
  because its final result landed after the results scan. 343 slices that had
  timed out without a final result were resubmitted on 2026-10-18. The earlier
  2026-10-18T15:06:27Z snapshot is kept unchanged as a record. No completion
  date is estimated.
- The public snapshots contain no usernames, account names, source paths,
  nodes, commands, or raw log streams.

## Acknowledgment

This work was completed in part with resources provided by the Auburn University Easley Cluster.
