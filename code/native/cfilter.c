/*
 * cfilter.c -- native edge-3-critical census filter.
 *
 * Reads graph6 lines (as emitted by `geng -Cq -d2 -D3 n`) on stdin, one graph
 * per line, and writes to stdout the graph6 lines of the SURVIVORS: the
 * nontrivial Delta=3 edge-critical non-overfull graphs.
 *
 * This is a bit-equal reimplementation of the Python reference pipeline in
 * codes/critical_graph_search/ (main.py _process_graph + criticality.py +
 * edge_coloring.py + density_filter.py + pruning.py). Every decision below cites
 * the Python line it mirrors. See docs/DECISIONS.md D-0002. It must reproduce the
 * Python survivor sets exactly (regression: order 13 -> 14, 15 -> 94, 17 -> 774).
 *
 * Survivor definition (main.py:44-82):
 *   maxdeg == 3  AND  passes_all_filters  AND  is_delta_critical  AND  !has_overfull
 * Plus an extra NECESSARY-ONLY Vizing-Adjacency-Lemma pre-filter (val_rejects, D-0006)
 * that never changes the survivor set (verified: drops 0/782186 real order-23 survivors)
 * but prunes ~87-100% of geng candidates before the expensive is_delta_critical DFS.
 *
 * Build:  cc -std=gnu11 -O3 -o cfilter cfilter.c        (modern gcc; NO -march=native --
 *         old gcc 4.8.5 -march=native SIGSEGVs on Easley's heterogeneous nodes, D-0005)
 * Usage:  geng -Cq -d2 -D3 <n> | ./cfilter
 *         geng -Cq -d2 -D3 <n> <res>/<mod> | ./cfilter     (Slurm modular split)
 *
 * Fixed to Delta = 3 (the census target): after the maxdeg==3 gate every graph
 * is 3-edge-coloured, so k = 3 throughout.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 64            /* graph6 supports up to 62 in the short form; census n <= ~30 */
#define K 3                /* Delta = 3 census: colour with 3 colours */

/* --- graph6 decode (nauty short form: first byte n+63, then bit-packed upper triangle) --- */
static int parse_graph6(const char *line, int *n_out, unsigned long long adj[MAXN]) {
  const unsigned char *p = (const unsigned char *)line;
  if (*p == '\0' || *p == '>') return 0;          /* skip empty / header lines */
  int n = (int)(*p) - 63;
  if (n < 1 || n > 62) return 0;
  p++;
  for (int i = 0; i < MAXN; i++) adj[i] = 0ULL;
  /* upper triangle read column-major: bit order is (0,1),(0,2),(1,2),(0,3),... i.e.
   * for j = 1..n-1, for i = 0..j-1 : one bit each, MSB-first within 6-bit groups. */
  int bitpos = 0;
  unsigned int cur = 0;
  int curbits = 0;
  for (int j = 1; j < n; j++) {
    for (int i = 0; i < j; i++) {
      if (curbits == 0) {
        unsigned int c = (unsigned int)(*p++);
        if (c < 63 || c > 126) return 0;
        cur = c - 63;
        curbits = 6;
      }
      int bit = (cur >> (curbits - 1)) & 1;
      curbits--;
      if (bit) {
        adj[i] |= (1ULL << j);
        adj[j] |= (1ULL << i);
      }
      bitpos++;
    }
  }
  (void)bitpos;
  *n_out = n;
  return 1;
}

/* degree of vertex i = popcount of adjacency row */
static inline int deg(unsigned long long m) { return __builtin_popcountll(m); }

/* --- Vizing's Adjacency Lemma pre-filter (Delta=3 specialization). ---
 * VAL (Vizing 1965; Stiebitz-Scheide-Toft-Favrholdt "Graph Edge Coloring" Thm 2.1):
 * for a Delta-critical graph, every edge uv has u adjacent to >= Delta-d(v)+1 vertices
 * of degree Delta. For Delta=3 (maxdeg==3 already gated), this collapses to a NECESSARY
 * vertex condition: EVERY vertex u has >= 2 neighbours of degree 3, AND 2*n2 <= n3.
 * Proof of the collapse (verified: 0/782186 real order-23 survivors rejected, floor=2):
 *   - edge uv, d(v)=2 => u needs >=2 degree-3 nbrs (v not counted) => u is deg-3 with its
 *     two OTHER nbrs deg-3; so no two deg-2 vertices adjacent, a deg-3 vertex has <=1 deg-2
 *     nbr; both give t3(u)>=2. edge uv, d(v)=3 => u needs >=1 (v itself), trivially t3(u)>=2
 *     unless... it is exactly the >=2 rule. Aggregating: 2*n2 <= n3.
 * NECESSARY-ONLY: never rejects a true Delta-critical survivor. Runs BEFORE the expensive
 * is_delta_critical DFS; prunes ~87-100% of geng candidates. Returns 1 if VAL REJECTS. */
static int val_rejects(int n, const unsigned long long adj[MAXN]) {
  unsigned long long deg3mask = 0ULL;
  int n2 = 0, n3 = 0;
  for (int i = 0; i < n; i++) {
    int d = deg(adj[i]);
    if (d == 3) { deg3mask |= (1ULL << i); n3++; }
    else if (d == 2) n2++;
  }
  if (2 * n2 > n3) return 1;                              /* aggregate VAL bound */
  for (int i = 0; i < n; i++)
    if (deg(adj[i] & deg3mask) < 2) return 1;             /* per-vertex VAL bound */
  return 0;
}

/* --- pruning.py: passes_all_filters (returns 1 if the graph SURVIVES pruning) --- */

/* is_bipartite via BFS 2-colouring (pruning.py:6-7) */
static int is_bipartite(int n, const unsigned long long adj[MAXN]) {
  signed char col[MAXN];
  for (int i = 0; i < n; i++) col[i] = -1;
  int stack[MAXN], sp;
  for (int s = 0; s < n; s++) {
    if (col[s] != -1) continue;
    col[s] = 0; sp = 0; stack[sp++] = s;
    while (sp) {
      int u = stack[--sp];
      unsigned long long m = adj[u];
      while (m) {
        int v = __builtin_ctzll(m); m &= m - 1;
        if (col[v] == -1) { col[v] = (signed char)(col[u] ^ 1); stack[sp++] = v; }
        else if (col[v] == col[u]) return 0;
      }
    }
  }
  return 1;
}

/* is_regular: all degrees equal (pruning.py:10-12) */
static int is_regular(int n, const unsigned long long adj[MAXN]) {
  int d0 = deg(adj[0]);
  for (int i = 1; i < n; i++) if (deg(adj[i]) != d0) return 0;
  return 1;
}

/* articulation-point (cut-vertex) existence via iterative DFS lowlink
 * (pruning.py:15-16, nx.articulation_points). Graph is connected here. */
static int has_cutvertex(int n, const unsigned long long adj[MAXN]) {
  int disc[MAXN], low[MAXN], parent[MAXN];
  unsigned long long rem[MAXN];
  for (int i = 0; i < n; i++) { disc[i] = -1; parent[i] = -1; }
  int timer = 0;
  for (int s = 0; s < n; s++) {
    if (disc[s] != -1) continue;
    /* iterative DFS from s */
    int root_children = 0;
    int stack[MAXN], sp = 0;
    stack[sp++] = s; disc[s] = low[s] = timer++; rem[s] = adj[s];
    while (sp) {
      int u = stack[sp - 1];
      if (rem[u]) {
        int v = __builtin_ctzll(rem[u]); rem[u] &= rem[u] - 1;
        if (disc[v] == -1) {
          parent[v] = u;
          if (u == s) root_children++;
          disc[v] = low[v] = timer++; rem[v] = adj[v];
          stack[sp++] = v;
        } else if (v != parent[u]) {
          if (disc[v] < low[u]) low[u] = disc[v];
        }
      } else {
        sp--;
        int p = parent[u];
        if (p != -1) {
          if (low[u] < low[p]) low[p] = low[u];
          if (p != s && low[u] >= disc[p]) return 1;   /* non-root articulation */
        }
      }
    }
    if (root_children > 1) return 1;                    /* root articulation */
  }
  return 0;
}

/* passes_all_filters (pruning.py:34-45); returns 1 if graph passes (survives). */
static int passes_all_filters(int n, const unsigned long long adj[MAXN]) {
  if (is_bipartite(n, adj)) return 0;                   /* :35 */
  if (is_regular(n, adj)) return 0;                     /* :37 */
  if (has_cutvertex(n, adj)) return 0;                  /* :39 */
  int dmax = 0, dmin = 1 << 30;
  for (int i = 0; i < n; i++) { int d = deg(adj[i]); if (d > dmax) dmax = d; if (d < dmin) dmin = d; }
  if (dmax >= n - 3) return 0;                          /* exceeds_chetwynd_hilton :19-22 */
  /* exceeds_arxiv_threshold :25-31 : dmax >= (2n + 5*dmin - 12)/3  (float compare) */
  double threshold = (2.0 * n + 5.0 * dmin - 12.0) / 3.0;
  if ((double)dmax >= threshold) return 0;
  return 1;
}

/* --- edge_coloring.py: exact backtracking 3-edge-colourability ---
 * Mirrors _is_k_edge_colorable_from_endpoints (edge_coloring.py:79-147).
 * edges[]: endpoint pairs; vmask[]: colour-usage bitmask per vertex; skip_idx: the
 * G-e edge index to omit (-1 for full graph). The yes/no result is a graph
 * invariant (independent of search order), so we reproduce the DECISION exactly. */

static int EC_ne;                       /* edge count */
static int EC_eu[3 * MAXN], EC_ev[3 * MAXN];  /* endpoints (subcubic => <= 3n/2 edges) */
static signed char EC_color[3 * MAXN];
static unsigned int EC_vmask[MAXN];
static int EC_active, EC_colored;

static inline unsigned int avail_mask(int e) {   /* edge_coloring.py:105-107 */
  unsigned int full = (1u << K) - 1u;
  return full & ~(EC_vmask[EC_eu[e]] | EC_vmask[EC_ev[e]]);
}

static int pick_uncolored(void) {                /* edge_coloring.py:109-122 (MRV) */
  int best = -1, bestsz = K + 1;
  for (int i = 0; i < EC_ne; i++) {
    if (EC_color[i] != -1) continue;
    int sz = __builtin_popcount(avail_mask(i));
    if (sz < bestsz) { best = i; bestsz = sz; if (sz <= 1) break; }
  }
  return best;
}

static int ec_dfs(void) {                        /* edge_coloring.py:124-145 */
  if (EC_colored == EC_active) return 1;
  int e = pick_uncolored();
  unsigned int dom = avail_mask(e);
  if (dom == 0) return 0;
  int u = EC_eu[e], v = EC_ev[e];
  while (dom) {                                  /* iter_colors ascending :97-103 */
    unsigned int lsb = dom & (~dom + 1u);
    int color = __builtin_ctz(lsb);
    dom ^= lsb;
    unsigned int bit = 1u << color;
    EC_color[e] = (signed char)color;
    EC_vmask[u] |= bit; EC_vmask[v] |= bit; EC_colored++;
    if (ec_dfs()) return 1;
    EC_colored--; EC_vmask[u] ^= bit; EC_vmask[v] ^= bit; EC_color[e] = -1;
  }
  return 0;
}

/* is 3-edge-colourable with edge skip_idx omitted (skip_idx=-1 => full graph). */
static int is_k_colorable(int n, int skip_idx) {
  if (EC_ne == 0 || (EC_ne == 1 && skip_idx == 0)) return 1;   /* :86-87 */
  for (int i = 0; i < EC_ne; i++) EC_color[i] = -1;
  if (skip_idx >= 0) EC_color[skip_idx] = -2;
  for (int i = 0; i < n; i++) EC_vmask[i] = 0;
  EC_active = EC_ne - (skip_idx >= 0 ? 1 : 0);
  EC_colored = 0;
  return ec_dfs();
}

/* build the endpoint arrays from adjacency (matches _prepare_endpoints:71-76:
 * vertices already 0..n-1 contiguous from graph6, edges normalised u<v). */
static void build_edges(int n, const unsigned long long adj[MAXN]) {
  EC_ne = 0;
  for (int u = 0; u < n; u++) {
    unsigned long long m = adj[u] >> (u + 1);
    int base = u + 1;
    while (m) {
      int off = __builtin_ctzll(m); m &= m - 1;
      int v = base + off;
      EC_eu[EC_ne] = u; EC_ev[EC_ne] = v; EC_ne++;
    }
  }
}

/* is_delta_critical (criticality.py:13-33). Assumes maxdeg==3 already checked and
 * geng gave a connected, min-degree>=2, bridgeless (biconnected) graph; we still
 * do the colourability core exactly. Connectivity/min-deg/bridge are guaranteed by
 * geng -Cq -d2 (biconnected => connected, no bridge, min-degree>=2), matching the
 * Python early-returns which would all pass here. */
static int is_delta_critical(int n, const unsigned long long adj[MAXN]) {
  build_edges(n, adj);
  if (is_k_colorable(n, -1)) return 0;             /* G must NOT be 3-colourable :27-28 */
  for (int e = 0; e < EC_ne; e++)                  /* every G-e MUST be 3-colourable :30-32 */
    if (!is_k_colorable(n, e)) return 0;
  return 1;
}

/* --- density_filter.py: has_overfull_subgraph fast (density_filter.py:74-93) ---
 * Odd subset S of size r is overfull iff edge_count(S) > delta*(r/2), strict >.
 * Iterate r = 1,3,5,...,n; enumerate all C(n,r) subsets; stop on first violation. */

/* enumerate all r-subsets of {0..n-1} via Gosper's hack; count internal edges by
 * bitmask; return 1 if any odd subset is overfull (delta = 3). */
static int has_overfull(int n, const unsigned long long adj[MAXN]) {
  const int delta = 3;
  for (int r = 1; r <= n; r += 2) {
    int threshold = delta * (r / 2);                 /* delta*(r//2) :86 */
    /* Gosper: iterate r-bit subsets of an n-bit universe */
    unsigned long long sub = (r <= 63) ? ((r == 0) ? 0ULL : ((1ULL << r) - 1ULL)) : 0ULL;
    unsigned long long limit = (n >= 64) ? ~0ULL : (1ULL << n);
    while (sub < limit) {
      /* count edges inside subset `sub` */
      int ecount = 0;
      unsigned long long rem = sub;
      while (rem) {
        int idx = __builtin_ctzll(rem); rem &= rem - 1;
        ecount += __builtin_popcountll(adj[idx] & rem);
        if (ecount > threshold) break;               /* early: cannot un-exceed */
      }
      if (ecount > threshold) return 1;              /* strict > :88 */
      /* Gosper's hack: next subset with same popcount */
      unsigned long long c = sub & (~sub + 1ULL);
      unsigned long long rr = sub + c;
      sub = (((sub ^ rr) >> 2) / c) | rr;
      if (sub == 0) break;
    }
  }
  return 0;
}

int main(void) {
  char *line = NULL;
  size_t cap = 0;
  ssize_t len;
  unsigned long long adj[MAXN];
  int n;
  /* larger stdout buffer for throughput */
  static char outbuf[1 << 20];
  setvbuf(stdout, outbuf, _IOFBF, sizeof(outbuf));

  /* Census scale counters (emitted to stderr at EOF; stdout stays pure survivor
   * graph6 so the Python pipeline that consumes stdout is unaffected).
   *   read       = graph6 lines consumed from geng (the raw candidate population)
   *   maxdeg3    = graphs with maxdeg == 3 (Delta==3 gate passed)
   *   val_pass   = graphs surviving the Vizing-Adjacency-Lemma pre-filter
   *   filt_pass  = graphs surviving passes_all_filters (structural pruning)
   *   critical   = Delta-critical graphs (before overfull test)
   *   survivors  = non-overfull Delta-critical survivors (== stdout line count)
   * These recover the metadata the streaming C filter previously discarded, so a
   * post-hoc count no longer requires re-running geng over ~10^11 graphs. */
  unsigned long long c_read = 0, c_maxdeg3 = 0, c_val = 0,
                     c_filt = 0, c_crit = 0, c_surv = 0;

  while ((len = getline(&line, &cap, stdin)) != -1) {
    if (len > 0 && line[len - 1] == '\n') line[--len] = '\0';
    if (line[0] == '\0' || line[0] == '>') continue;
    if (!parse_graph6(line, &n, adj)) continue;
    c_read++;

    /* main.py:51 -- maxdeg must equal delta (3) */
    int dmax = 0;
    for (int i = 0; i < n; i++) { int d = deg(adj[i]); if (d > dmax) dmax = d; }
    if (dmax != 3) continue;
    c_maxdeg3++;

    if (val_rejects(n, adj)) continue;               /* Vizing Adjacency Lemma (necessary-only) */
    c_val++;
    if (!passes_all_filters(n, adj)) continue;       /* main.py:54 */
    c_filt++;
    if (!is_delta_critical(n, adj)) continue;        /* main.py:57 */
    c_crit++;
    if (has_overfull(n, adj)) continue;              /* main.py:60-67 */

    /* survivor */
    c_surv++;
    fputs(line, stdout);
    fputc('\n', stdout);
  }
  free(line);

  /* Machine-readable scale summary on stderr. Single line, stable key=value form
   * so main.py can parse it without disturbing the survivor stream on stdout. */
  fflush(stdout);
  fprintf(stderr,
          "CFILTER_STATS read=%llu maxdeg3=%llu val_pass=%llu filt_pass=%llu "
          "critical=%llu survivors=%llu\n",
          c_read, c_maxdeg3, c_val, c_filt, c_crit, c_surv);
  return 0;
}
