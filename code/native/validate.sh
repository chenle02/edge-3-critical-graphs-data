#!/usr/bin/env bash
# Bit-equality regression for the native census filter (docs/DECISIONS.md D-0002).
#
# Proves the C filter (cfilter) keeps EXACTLY the same survivors as the Python
# reference pipeline, for orders 13, 15, 17 (known counts 14, 94, 774). Because
# the two emit the same graphs in different graph6 labelings, we compare the
# nauty CANONICAL forms (via labelg), which is the true graph-identity check.
#
# Usage:  ./validate.sh            (uses geng + labelg on PATH or ~/bin)
# Exit 0 iff every order matches count AND canonical survivor set.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
GENG="${GENG:-$(command -v geng || echo "$HOME/bin/geng")}"
LABELG="${LABELG:-$(command -v labelg || echo "$HOME/bin/labelg")}"
CF="$HERE/cfilter"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

declare -A EXPECT=( [13]=14 [15]=94 [17]=774 )
rc=0

echo "== build =="
# Portable build (no -march=native): matches the Easley production build. -march=native
# under old gcc (4.8.5) on Easley's heterogeneous nodes intermittently SIGSEGVs (D-0005),
# and the speedup is algorithmic not vectorization, so plain -O3 is both safe and fast.
cc -std=gnu11 -O3 -Wall -Wextra -o "$CF" "$HERE/cfilter.c"
echo "   built $CF  ($(cc --version 2>&1 | head -1))"

for O in 13 15 17; do
  echo "== order $O (expect ${EXPECT[$O]}) =="
  "$GENG" -Cq -d2 -D3 "$O" 2>/dev/null > "$TMP/geng_$O.g6"
  # C filter survivors -> canonical
  "$CF" < "$TMP/geng_$O.g6" | "$LABELG" -q 2>/dev/null | sort > "$TMP/c_can_$O.txt"
  # Python reference survivors -> canonical
  python3 "$HERE/pyref.py" < "$TMP/geng_$O.g6" | "$LABELG" -q 2>/dev/null | sort > "$TMP/py_can_$O.txt"
  cn=$(wc -l < "$TMP/c_can_$O.txt")
  pn=$(wc -l < "$TMP/py_can_$O.txt")
  if [[ "$cn" == "${EXPECT[$O]}" && "$pn" == "${EXPECT[$O]}" ]] && diff -q "$TMP/c_can_$O.txt" "$TMP/py_can_$O.txt" >/dev/null; then
    echo "   PASS: C=$cn Python=$pn canonical-identical"
  else
    echo "   FAIL: C=$cn Python=$pn (expected ${EXPECT[$O]})"
    diff "$TMP/c_can_$O.txt" "$TMP/py_can_$O.txt" | head -10 || true
    rc=1
  fi
done

[[ $rc -eq 0 ]] && echo "ALL PASS -- C filter is bit-equal to the Python reference." || echo "REGRESSION."
exit $rc
