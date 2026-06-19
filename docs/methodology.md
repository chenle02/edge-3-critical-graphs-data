# Methodology

The census tests candidate subcubic graphs through a five-stage pipeline. The output survivors are exactly the connected, nontrivial edge-chromatic 3-critical graphs that pass all filters.

## Stage 1: generate 2-connected subcubic graphs

Candidate graphs of order `n` are generated with nauty's `geng`:

```bash
geng -Cq -d2 -D3 n
```

The flags mean:

- `-C` — restrict generation to 2-connected (biconnected) graphs.
- `-q` — quiet output, suitable for pipeline processing.
- `-d2` — minimum degree at least 2.
- `-D3` — maximum degree at most 3.

## Stage 2: pruning filters

Two structural filters remove candidates that cannot be nontrivial 3-critical survivors:

1. **F1 bipartite filter** — discard bipartite candidates.
2. **F2 regular filter** — discard regular candidates.

These filters keep the later edge-coloring checks focused on the irregular nontrivial regime relevant to the paper.

## Stage 3: class-2 test

For each remaining graph, the pipeline tests whether it is Δ-edge-colorable. Since Δ = 3 throughout this census, any graph that admits a 3-edge-coloring is discarded. The retained candidates have chromatic index 4 and are class 2.

## Stage 4: edge-criticality test

The class-2 candidates are then tested for edge-criticality: deleting any edge must lower the chromatic index to 3. A graph that fails this test is not edge-chromatic 3-critical and is discarded.

## Stage 5: overfull-subgraph test

The final filter checks for 3-overfull subgraphs. Any candidate containing such a subgraph is considered trivial for this census and is removed. The survivors after this stage are the nontrivial 3-critical graphs reported in the data files.

## Theoretical context

The computational census is paired with the paper's characterization theorem and an order-25/order-27 impossibility result. The repository includes verification code and audit reports for the computational side, while the paper supplies the theoretical reduction and proof context connecting the census to the final classification statements.
