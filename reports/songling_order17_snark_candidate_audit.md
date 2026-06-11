# Audit of Songling's order-17 snark-deletion question

## Exact claim audited
- Original text: For some order 17 residues that have girth 4, and are cyclically 4-connected, are they come from the two order 18 snarks by deleting a vertex?
- Literal paraphrase: Among the current order-17 residue graphs, look only at those with girth 4 and cyclically 4-connected structure, then ask whether they come from deleting one vertex from one of the two order-18 snarks.
- Mathematical interpretation used here: First isolate the current order-17 residue graphs with girth 4 and no cyclic edge-cut of size 1, 2, or 3; only that filtered subfamily should be tested against order-18 snark vertex deletions.

## Current residue audit
- Order-17 residue graphs audited: 33
- Recomputed girth-4 graphs: 25
- Graphs with some cyclic 1-, 2-, or 3-edge-cut: 27
- Dossier girth/4-cycle mismatches found: 3

Current audited order-17 residue candidates: none.

## Conservative conclusion
- Every recomputed girth-4 graph in the current order-17 remaining residue still has at least one cyclic 1-, 2-, or 3-edge-cut.
- Therefore none of the current remaining residues satisfies Songling's girth-4 plus cyclically-4-connected gate.
- Hence the vertex-deletion test against the two order-18 snarks is vacuous for the current remaining residue.

## Dossier consistency note
- Girth metadata mismatch detected for: #325 (dossier girth 5 -> recomputed 4), #585 (dossier girth 5 -> recomputed 4), #616 (dossier girth 5 -> recomputed 4).
- Their 4-cycle counts agree under recomputation, so the inconsistency is in the stored girth field rather than in the 4-cycle counts for those rows.
