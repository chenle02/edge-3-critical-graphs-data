# Order-19 native replay audit

Date: 2026-07-28

This audit resolves the two-unit residual in the historical Order-19 scalar
pipeline ledger. It is a data-integrity check; the all-order characterization
theorem is independent of every finite census.

## Method

On Greenwood, the order-19 input was regenerated in eight disjoint nauty
prefix classes:

```text
geng -Cq -d2 -D3 19 m/8 | ./cfilter,  m = 0,...,7.
```

All eight parts exited with status zero. The C filter source is archived at
`code/native/cfilter.c` with SHA-256
`7f47697ffb6b7fb65e693342e1563a1553dafe3d5023444f7f23902c08d955de`.
The complete per-part counters are in
`reports/order19_native_replay_20260728.json`.

## Exact result

| Counter | Fresh replay |
|---|---:|
| graph6 records read | 51,643,246 |
| exact maximum degree 3 | 51,643,245 |
| VAL pass | 5,338,011 |
| structural-filter pass | 5,335,076 |
| 3-critical | 1,007,427 |
| non-overfull survivors | 6,984 |

The single graph that fails the exact maximum-degree-3 gate is the unique
cycle \(C_{19}\). This explains the systematic one-unit residual also seen at
the other orders: `geng -D3` imposes an upper bound, whereas the census then
requires maximum degree exactly 3.

The archived Order-19 run was interrupted and resumed several times. Its
historical scalar subcounters have one additional missing unit, arising from
the old checkpoint transaction rather than from an untested output class.
The pipeline now masks SIGINT/SIGTERM while updating a graph's processed
counter, prefix fingerprint, and classification counters, so a checkpoint
cannot split that transaction.

## Survivor-set comparison

Both the archived JSON survivors and the fresh native survivors were
canonicalized with `labelg`, sorted, and deduplicated.

| Check | Result |
|---|---:|
| archived canonical survivors | 6,984 |
| fresh canonical survivors | 6,984 |
| set difference | 0 |
| canonical SHA-256, both sets | `79d4bf66bf9458da1060d0659eeaef25a28c0704ad49e96c622fe1f54fbde9b1` |

The fresh canonical stream is archived as
`results/order_19_delta_3_native_replay.canonical.g6.gz`, SHA-256
`61a682f6b4d7f9ca4ea5feedc0fa9a71c71e98f23618555175a6ec8c70409716`.

Thus the historical interruption changed neither the exact critical count nor
the nontrivial survivor set.
