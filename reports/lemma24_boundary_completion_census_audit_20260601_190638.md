# Lemma 2.4 boundary-pair completion census audit

Generated: 2026-06-01T19:06:38

## Scope
- Orders tested: [13, 15, 17, 19]
- Minimum component order: 5
- For each qualifying cyclic-3-cut side `H`, relabel the three boundary degree-2 vertices as `0,1,2`.
- For each non-existing boundary pair, add the simple edge and test whether the completion is Delta-critical.
- Existing boundary edges are recorded as `already_edge` and are not counted as added-edge completions.
- Guardrail: do not send Songling-facing prose from this audit without a fresh review/honesty gate.
- Caveat: this is a finite audit of the implemented simple boundary-pair completion condition, not a theorem for unaudited conventions.

## Summary
- Qualifying H components tested: 3814
- Components without a Delta-critical boundary-pair completion: 0
- All tested H have a Delta-critical boundary-pair completion: True
- Early stop: False

## Sources
- Order 13: `codes/critical_graph_search/results/order_13_delta_3.json`
- Order 15: `codes/critical_graph_search/results/order_15_delta_3.json`
- Order 17: `codes/critical_graph_search/results/order_17_delta_3.json`
- Order 19: `codes/critical_graph_search/results/order_19_delta_3.json`

## By order

### Order 13
- Source survivor count: 14
- Skipped because not cyclically 3-edge-connected: 8
- Graphs with qualifying H: 3
- Qualifying H components: 3
- Components with a Delta-critical boundary-pair completion: 3
- Components without a Delta-critical boundary-pair completion: 0
- Positive non-edge pair count distribution: {'2': 2, '3': 1}

### Order 15
- Source survivor count: 94
- Skipped because not cyclically 3-edge-connected: 65
- Graphs with qualifying H: 26
- Qualifying H components: 33
- Components with a Delta-critical boundary-pair completion: 33
- Components without a Delta-critical boundary-pair completion: 0
- Positive non-edge pair count distribution: {'2': 20, '3': 13}

### Order 17
- Source survivor count: 774
- Skipped because not cyclically 3-edge-connected: 554
- Graphs with qualifying H: 209
- Qualifying H components: 345
- Components with a Delta-critical boundary-pair completion: 345
- Components without a Delta-critical boundary-pair completion: 0
- Positive non-edge pair count distribution: {'1': 5, '2': 195, '3': 145}

### Order 19
- Source survivor count: 6984
- Skipped because not cyclically 3-edge-connected: 5102
- Graphs with qualifying H: 1758
- Qualifying H components: 3433
- Components with a Delta-critical boundary-pair completion: 3433
- Components without a Delta-critical boundary-pair completion: 0
- Positive non-edge pair count distribution: {'1': 81, '2': 1762, '3': 1590}
