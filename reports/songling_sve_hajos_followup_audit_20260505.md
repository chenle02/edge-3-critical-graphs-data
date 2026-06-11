# Songling S-v-e ordinary-Hajos follow-up audit

## Conclusion

Yes, under the same standard ordinary-Hajos formalization used in the remaining-132 operation report, all 22 raw `S-v-e` critical witnesses have ordinary-Hajos witnesses.

- Raw S-v-e targets checked: `22`
- Raw S-v-e targets with ordinary-Hajos witness: `22`
- Unique survivor census classes: `7`
- Unique survivor census classes with ordinary-Hajos witness: `7`
- Unique targets by order: `{'17': [195, 196], '19': [1910, 1911, 1913, 1917, 3026]}`
- Candidate count: `828`; exact isomorphism checks: `3816`

## Scope / caveat

Ordinary-Hajos formalization: Delete one edge from each smaller Delta=3 critical survivor, identify one endpoint from each deleted edge, and add an edge between the two non-identified endpoints; all endpoint orientations are tested.

The statement is an existence statement for these 22 raw witness rows (7 unique survivor classes), not a claim that ordinary Hajos is the unique way to obtain them and not an exhaustive theorem about all critical subgraphs.

The per-row Hajos witness counts below count labeled/oriented construction hits under the implemented search and can include automorphism/orientation duplicates; they should not be read as counts of distinct decompositions.

## Source-pair summary

| target order | source pair | candidates | iso checks | unique classes hit |
|---:|---|---:|---:|---|
| 17 | 5+13 | 0 | 0 | [] |
| 17 | 7+11 | 0 | 0 | [] |
| 17 | 9+9 | 252 | 2520 | [[17, 195], [17, 196]] |
| 19 | 5+15 | 0 | 0 | [] |
| 19 | 7+13 | 0 | 0 | [] |
| 19 | 9+11 | 576 | 1296 | [[19, 1910], [19, 1911], [19, 1913], [19, 1917], [19, 3026]] |

## Unique census target examples

| target | raw panels | sample Hajos witness |
|---|---|---|
| order 17 #195 | [7, 10] | 9#1 edge [0, 3] + 9#1 edge [0, 3]; identify endpoints 0,0 |
| order 17 #196 | [1, 2, 3, 4, 5, 6, 8, 9] | 9#1 edge [0, 3] + 9#1 edge [1, 6]; identify endpoints 0,0 |
| order 19 #1910 | [21] | 9#1 edge [0, 3] + 11#1 edge [2, 9]; identify endpoints 0,0 |
| order 19 #1911 | [15] | 9#1 edge [0, 3] + 11#1 edge [2, 6]; identify endpoints 0,0 |
| order 19 #1913 | [13, 18, 19] | 9#1 edge [1, 6] + 11#1 edge [2, 6]; identify endpoints 0,1 |
| order 19 #1917 | [12, 20, 22] | 9#1 edge [0, 3] + 11#2 edge [6, 10]; identify endpoints 0,0 |
| order 19 #3026 | [11, 14, 16, 17] | 9#1 edge [0, 3] + 11#2 edge [2, 6]; identify endpoints 0,0 |

## Raw-row table

| raw panel | target | source S-v-e witness | Hajos witness count |
|---:|---|---|---:|
| 1 | order 17 #196 | S18 class 1, delete v=3, then e=[5, 10] | 144 |
| 2 | order 17 #196 | S18 class 1, delete v=5, then e=[3, 9] | 144 |
| 3 | order 17 #196 | S18 class 1, delete v=6, then e=[0, 7] | 144 |
| 4 | order 17 #196 | S18 class 1, delete v=7, then e=[6, 12] | 144 |
| 5 | order 17 #196 | S18 class 2, delete v=0, then e=[7, 13] | 144 |
| 6 | order 17 #196 | S18 class 2, delete v=2, then e=[5, 14] | 144 |
| 7 | order 17 #195 | S18 class 2, delete v=5, then e=[2, 8] | 108 |
| 8 | order 17 #196 | S18 class 2, delete v=8, then e=[5, 11] | 144 |
| 9 | order 17 #196 | S18 class 2, delete v=10, then e=[3, 13] | 144 |
| 10 | order 17 #195 | S18 class 2, delete v=13, then e=[0, 10] | 108 |
| 11 | order 19 #3026 | S20 class 1, delete v=0, then e=[2, 15] | 24 |
| 12 | order 19 #1917 | S20 class 1, delete v=15, then e=[0, 14] | 12 |
| 13 | order 19 #1913 | S20 class 2, delete v=2, then e=[7, 18] | 24 |
| 14 | order 19 #3026 | S20 class 2, delete v=15, then e=[3, 18] | 24 |
| 15 | order 19 #1911 | S20 class 2, delete v=18, then e=[2, 15] | 36 |
| 16 | order 19 #3026 | S20 class 3, delete v=6, then e=[7, 19] | 24 |
| 17 | order 19 #3026 | S20 class 3, delete v=7, then e=[6, 18] | 24 |
| 18 | order 19 #1913 | S20 class 4, delete v=9, then e=[6, 12] | 24 |
| 19 | order 19 #1913 | S20 class 4, delete v=12, then e=[9, 16] | 24 |
| 20 | order 19 #1917 | S20 class 5, delete v=2, then e=[7, 19] | 12 |
| 21 | order 19 #1910 | S20 class 5, delete v=7, then e=[2, 18] | 12 |
| 22 | order 19 #1917 | S20 class 5, delete v=18, then e=[7, 14] | 12 |
