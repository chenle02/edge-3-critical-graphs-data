#!/usr/bin/env python3
"""Exhaust the projected three-boundary states in four-corner Pattern I.

The Pattern-I connector has two subdivided channels and one direct channel.
For boundary color triples ``left`` and ``right`` its three relations are

    left[0] != right[0],
    left[1] != right[1],
    left[2] == right[2].

Boundary triples are considered up to a permutation of the three colors.  The
five equality types are ``M=AAA``, ``P12=AAB``, ``P13=ABA``, ``P23=ABB``,
and ``R=ABC``.

If the whole connector is uncolorable but deleting an edge from each of the
three channels makes it colorable, the two nonempty shore-state families must
be one of six pairs.  This script verifies that finite classification exactly.
The accompanying proof note supplies the graph-theoretic Kempe argument that
rules out every classified pair.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections.abc import Iterable

TYPE_ORDER = ("M", "P12", "P13", "P23", "R")
REPRESENTATIVES = {
    "M": (0, 0, 0),
    "P12": (0, 0, 1),
    "P13": (0, 1, 0),
    "P23": (0, 1, 1),
    "R": (0, 1, 2),
}


def color_orbit(boundary_type: str) -> frozenset[tuple[int, int, int]]:
    """Return all triples obtained by relabeling colors, not boundary ports."""
    representative = REPRESENTATIVES[boundary_type]
    return frozenset(
        tuple(permutation[color] for color in representative)
        for permutation in itertools.permutations(range(3))
    )


COLOR_ORBITS = {
    boundary_type: color_orbit(boundary_type)
    for boundary_type in TYPE_ORDER
}


def connector_compatible(
    left_type: str,
    right_type: str,
    *,
    dropped_relations: Iterable[int] = (),
) -> bool:
    """Test compatibility after dropping any relations numbered 1, 2, or 3."""
    dropped = frozenset(dropped_relations)
    if not dropped <= {1, 2, 3}:
        raise ValueError("relations are numbered 1, 2, and 3")

    def relations(
        left: tuple[int, int, int],
        right: tuple[int, int, int],
    ) -> tuple[bool, bool, bool]:
        return (
            left[0] != right[0],
            left[1] != right[1],
            left[2] == right[2],
        )

    return any(
        all(
            relation
            for index, relation in enumerate(relations(left, right), start=1)
            if index not in dropped
        )
        for left in COLOR_ORBITS[left_type]
        for right in COLOR_ORBITS[right_type]
    )


def nonempty_type_families() -> list[frozenset[str]]:
    """List the 31 nonempty families in a stable order."""
    return [
        frozenset(
            boundary_type
            for index, boundary_type in enumerate(TYPE_ORDER)
            if mask & (1 << index)
        )
        for mask in range(1, 1 << len(TYPE_ORDER))
    ]


def critical_family_pairs() -> list[tuple[frozenset[str], frozenset[str]]]:
    """Classify state families rejected intact but admitted after every drop."""
    solutions: list[tuple[frozenset[str], frozenset[str]]] = []
    for left_family in nonempty_type_families():
        for right_family in nonempty_type_families():
            if any(
                connector_compatible(left_type, right_type)
                for left_type in left_family
                for right_type in right_family
            ):
                continue
            if all(
                any(
                    connector_compatible(
                        left_type,
                        right_type,
                        dropped_relations=(relation,),
                    )
                    for left_type in left_family
                    for right_type in right_family
                )
                for relation in (1, 2, 3)
            ):
                solutions.append((left_family, right_family))
    return solutions


def boundary_type(colors: tuple[int, int, int]) -> str:
    """Return the equality type of a three-color boundary triple."""
    first, second, third = colors
    if first == second == third:
        return "M"
    if first == second:
        return "P12"
    if first == third:
        return "P13"
    if second == third:
        return "P23"
    return "R"


def proper_kempe_subsets_change_type(boundary_type_name: str) -> bool:
    """Verify the local equality-pattern step in the Kempe argument.

    For ``M`` choose the two colors appearing in ``(A,A,A)`` after adjoining
    an unused color; for ``P12`` use the two displayed colors.  A bichromatic
    component can meet the three boundary semiedges in any nonempty proper
    subset, but never in all three.  Swapping the two colors on such a component
    must change the projected equality type.
    """
    if boundary_type_name == "M":
        colors = (0, 0, 0)
    elif boundary_type_name == "P12":
        colors = (0, 0, 1)
    else:
        raise ValueError("the certificate is only needed for M and P12")

    original = boundary_type(colors)
    for mask in range(1, 7):
        swapped = tuple(
            1 - color if mask & (1 << index) else color
            for index, color in enumerate(colors)
        )
        if boundary_type(swapped) == original:
            return False
    return True


def report() -> dict[str, object]:
    pairs = critical_family_pairs()
    return {
        "type_order": TYPE_ORDER,
        "relations": {
            "1": "left[0] != right[0]",
            "2": "left[1] != right[1]",
            "3": "left[2] == right[2]",
        },
        "critical_family_pair_count": len(pairs),
        "critical_family_pairs": [
            {
                "left": [
                    name for name in TYPE_ORDER if name in left_family
                ],
                "right": [
                    name for name in TYPE_ORDER if name in right_family
                ],
            }
            for left_family, right_family in pairs
        ],
        "every_pair_forces_forbidden_singleton": all(
            left_family in (frozenset({"M"}), frozenset({"P12"}))
            or right_family in (frozenset({"M"}), frozenset({"P12"}))
            for left_family, right_family in pairs
        ),
        "kempe_pattern_change": {
            boundary_type_name: proper_kempe_subsets_change_type(
                boundary_type_name
            )
            for boundary_type_name in ("M", "P12")
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation (default: 2)",
    )
    args = parser.parse_args()
    print(json.dumps(report(), indent=args.indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
