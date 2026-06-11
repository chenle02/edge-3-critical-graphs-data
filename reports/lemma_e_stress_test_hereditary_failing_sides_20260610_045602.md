# Lemma E stress test: exhaustive hereditary failing tight-side hunt

Generated: 2026-06-10T04:56:02

## Question
A Lemma E counterexample needs a hereditarily failing tight side (the side
and ALL its qualifying tight sub-sides lack Delta-critical boundary-pair
completions, and the side passes the local embeddability conditions).
This run enumerates ALL tight-side shapes (degree sequence 3^{n-3} 2^3,
connected, no cyclic cut < 3) at the tested orders via geng — exhaustive,
unlike the random A13 probes (~3,400 sides/order).

## Summary
- Orders (exhaustive): [7, 9, 11, 13]
- Total candidates: 5096
- Failing sides (no critical completion): 4
- **Hereditarily failing sides (Lemma E seeds): 0**
- Conclusion: any Lemma E counterexample must contain a failing minimal tight side of order >= 15.

## By order

| n | candidates | cyclic-cut<3 skip | not colorable | completes | failing | not embeddable | rescued by sub-side | HEREDITARY |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 10 | 4 | 0 | 6 | 0 | 0 | 0 | 0 |
| 9 | 63 | 34 | 1 | 28 | 0 | 0 | 0 | 0 |
| 11 | 482 | 279 | 2 | 200 | 1 | 0 | 1 | 0 |
| 13 | 4541 | 2514 | 12 | 2012 | 3 | 0 | 3 | 0 |

## Failing sides detail

- order 11, graph6 below: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
  ```text
  J?`DAaoJ?s?
  ```
- order 13, `L??ED?WSHgD_BO`: embeddable=True, sub-sides=3, some sub-side completes=True, HEREDITARY=False
- order 13, `L?AAD?oq?[B_S_`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False
- order 13, `L?AAD?WSJO@oK_`: embeddable=True, sub-sides=2, some sub-side completes=True, HEREDITARY=False

## Guardrails
- Finite exhaustive local evidence; not an all-order theorem.
- A hereditarily failing side is only a counterexample SEED; refuting
  Lemma E additionally requires an ambient critical embedding.
- Do not send Songling-facing prose from this audit without a fresh gate.

JSON sibling: `lemma_e_stress_test_hereditary_failing_sides_20260610_045602.json`
