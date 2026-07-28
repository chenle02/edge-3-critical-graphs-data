#!/usr/bin/env python3
"""Exhaust the projected boundary-state constraints in Pattern II.

Pattern II has three boundary ports on each cyclic shore ``X`` and ``W``
and four boundary ports on the middle corner ``Y``.  Number the ports so
that port 0 of each shore is incident with the path through the degree-2
vertex ``z`` and ports 1,2 are incident with ``Y``.  The five connector
relations are

    X[0] != W[0],
    X[1] == Y[0],
    X[2] == Y[1],
    W[1] == Y[2],
    W[2] == Y[3].

The intact connector must be uncolorable, while deleting an edge from any
one of its five channels must leave the other four relations satisfiable.

The script also imposes a necessary Kempe-component relaxation.  For each
boundary state and each pair of colors, the boundary ends met by the
bichromatic components must admit a partition into singleton or paired
blocks.  Swapping any collection of those components must produce another
state in the same family.  The partitions for the three color pairs are
allowed to be chosen independently, so passing this test is necessary but
not sufficient for realization by one multipole.

Consequently the output is a rigorous finite *necessary-condition*
classification.  It is not a realizability theorem and by itself does not
exclude Pattern II.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable
from functools import lru_cache
import itertools
import json

ColorType = tuple[int, ...]
StateFamily = frozenset[ColorType]
BlockPartition = tuple[tuple[int, ...], ...]

FULL_COMPATIBILITY_BIT = 1 << 5
ALL_DROPS_MASK = (1 << 5) - 1


def restricted_growth_types(boundary_size: int) -> tuple[ColorType, ...]:
    """Return equality types on ``boundary_size`` ports using at most 3 colors."""
    if boundary_size < 1:
        raise ValueError("boundary_size must be positive")

    result: list[ColorType] = []

    def extend(prefix: ColorType) -> None:
        if len(prefix) == boundary_size:
            result.append(prefix)
            return
        upper_bound = min(3, max(prefix) + 2 if prefix else 1)
        for color in range(upper_bound):
            extend(prefix + (color,))

    extend(())
    return tuple(result)


THREE_TYPES = restricted_growth_types(3)
FOUR_TYPES = restricted_growth_types(4)

MONOCHROMATIC = (0, 0, 0)
PAIR_23 = (0, 1, 1)
RAINBOW = (0, 1, 2)

RAINBOW_FAMILY = frozenset({RAINBOW})
K_FAMILY = frozenset({MONOCHROMATIC, PAIR_23, RAINBOW})
CROSS_FAMILY = frozenset({(0, 1, 0, 1), (0, 1, 1, 0)})


def canonical_type(colors: Iterable[int]) -> ColorType:
    """Canonicalize a color tuple by order of first appearance."""
    relabeling: dict[int, int] = {}
    canonical: list[int] = []
    for color in colors:
        if color not in relabeling:
            relabeling[color] = len(relabeling)
        canonical.append(relabeling[color])
    return tuple(canonical)


@lru_cache(maxsize=None)
def color_orbit(boundary_type: ColorType) -> frozenset[ColorType]:
    """Return all tuples obtained by relabeling colors, never boundary ports."""
    return frozenset(
        tuple(permutation[color] for color in boundary_type)
        for permutation in itertools.permutations(range(3))
    )


@lru_cache(maxsize=None)
def singleton_pair_partitions(
    positions: tuple[int, ...],
) -> tuple[BlockPartition, ...]:
    """Partition ordered positions into blocks of size one or two."""
    if not positions:
        return ((),)

    first = positions[0]
    rest = positions[1:]
    partitions: list[BlockPartition] = []

    for tail in singleton_pair_partitions(rest):
        partitions.append(((first,),) + tail)

    for partner_index, partner in enumerate(rest):
        remaining = rest[:partner_index] + rest[partner_index + 1 :]
        for tail in singleton_pair_partitions(remaining):
            partitions.append(((first, partner),) + tail)

    return tuple(partitions)


def swapped_boundary_types(
    boundary_type: ColorType,
    color_pair: tuple[int, int],
    partition: BlockPartition,
) -> frozenset[ColorType]:
    """Return types produced by swapping any nonempty set of blocks."""
    first_color, second_color = color_pair
    results: set[ColorType] = set()

    for block_mask in range(1, 1 << len(partition)):
        colors = list(boundary_type)
        for block_index, block in enumerate(partition):
            if not block_mask & (1 << block_index):
                continue
            for position in block:
                if colors[position] == first_color:
                    colors[position] = second_color
                elif colors[position] == second_color:
                    colors[position] = first_color
                else:
                    raise ValueError("partition contains an irrelevant position")
        results.add(canonical_type(colors))

    return frozenset(results)


def passes_kempe_partition_relaxation(family: StateFamily) -> bool:
    """Test the necessary, independently-partitioned Kempe closure condition."""
    if not family:
        return False

    for boundary_type in family:
        for color_pair in itertools.combinations(range(3), 2):
            positions = tuple(
                index
                for index, color in enumerate(boundary_type)
                if color in color_pair
            )
            if not any(
                swapped_boundary_types(
                    boundary_type,
                    color_pair,
                    partition,
                )
                <= family
                for partition in singleton_pair_partitions(positions)
            ):
                return False
    return True


@lru_cache(maxsize=None)
def kempe_admissible_families(
    boundary_size: int,
) -> tuple[StateFamily, ...]:
    """Enumerate nonempty families passing the necessary Kempe relaxation."""
    types = restricted_growth_types(boundary_size)
    return tuple(
        family
        for mask in range(1, 1 << len(types))
        if passes_kempe_partition_relaxation(
            family := frozenset(
                boundary_type
                for index, boundary_type in enumerate(types)
                if mask & (1 << index)
            )
        )
    )


def connector_relations(
    x_colors: ColorType,
    w_colors: ColorType,
    y_colors: ColorType,
) -> tuple[bool, bool, bool, bool, bool]:
    """Evaluate the five Pattern-II connector relations."""
    return (
        x_colors[0] != w_colors[0],
        x_colors[1] == y_colors[0],
        x_colors[2] == y_colors[1],
        w_colors[1] == y_colors[2],
        w_colors[2] == y_colors[3],
    )


@lru_cache(maxsize=None)
def type_compatibility_flags(
    x_type: ColorType,
    w_type: ColorType,
    y_type: ColorType,
) -> int:
    """Encode full compatibility and each one-relation-drop compatibility."""
    flags = 0
    for x_colors, w_colors, y_colors in itertools.product(
        color_orbit(x_type),
        color_orbit(w_type),
        color_orbit(y_type),
    ):
        relations = connector_relations(x_colors, w_colors, y_colors)
        if all(relations):
            flags |= FULL_COMPATIBILITY_BIT
        for dropped_relation in range(5):
            if all(
                relation
                for index, relation in enumerate(relations)
                if index != dropped_relation
            ):
                flags |= 1 << dropped_relation
    return flags


def family_compatibility_flags(
    x_family: StateFamily,
    w_family: StateFamily,
    y_family: StateFamily,
) -> int:
    """Union the compatibility flags over a triple of state families."""
    flags = 0
    for x_type, w_type, y_type in itertools.product(
        x_family,
        w_family,
        y_family,
    ):
        flags |= type_compatibility_flags(x_type, w_type, y_type)
    return flags


@lru_cache(maxsize=1)
def critical_family_triples(
) -> tuple[tuple[StateFamily, StateFamily, StateFamily], ...]:
    """Classify relaxed families rejected intact but admitted after every drop."""
    three_families = kempe_admissible_families(3)
    four_families = kempe_admissible_families(4)
    solutions: list[tuple[StateFamily, StateFamily, StateFamily]] = []

    for x_family in three_families:
        for w_family in three_families:
            flags_by_y_type: dict[ColorType, int] = {}
            for y_type in FOUR_TYPES:
                flags = 0
                for x_type, w_type in itertools.product(x_family, w_family):
                    flags |= type_compatibility_flags(
                        x_type,
                        w_type,
                        y_type,
                    )
                flags_by_y_type[y_type] = flags

            for y_family in four_families:
                flags = 0
                for y_type in y_family:
                    flags |= flags_by_y_type[y_type]
                if flags & FULL_COMPATIBILITY_BIT:
                    continue
                if flags & ALL_DROPS_MASK == ALL_DROPS_MASK:
                    solutions.append((x_family, w_family, y_family))

    return tuple(solutions)


def type_label(boundary_type: ColorType) -> str:
    """Render a restricted-growth type compactly."""
    return "".join(str(color) for color in boundary_type)


def family_labels(family: StateFamily) -> list[str]:
    """Render one state family in the canonical type order."""
    type_order = (
        THREE_TYPES if all(len(item) == 3 for item in family) else FOUR_TYPES
    )
    return [
        type_label(boundary_type)
        for boundary_type in type_order
        if boundary_type in family
    ]


def parity_feasible_with_deficits(
    boundary_type: ColorType,
    deficit_count: int,
) -> bool:
    """Test the cubic-multipole Parity Lemma for projected boundary data."""
    if deficit_count < 0:
        raise ValueError("deficit_count must be nonnegative")
    semiedge_count = len(boundary_type) + deficit_count
    required_odd_counts = sum(
        (semiedge_count - boundary_type.count(color)) % 2
        for color in range(3)
    )
    return (
        required_odd_counts <= deficit_count
        and (deficit_count - required_odd_counts) % 2 == 0
    )


def minimum_positive_deficits(family: StateFamily) -> int:
    """Return the least positive deficit count compatible with every type."""
    for deficit_count in itertools.count(1):
        if all(
            parity_feasible_with_deficits(boundary_type, deficit_count)
            for boundary_type in family
        ):
            return deficit_count
    raise AssertionError("unreachable")


def report() -> dict[str, object]:
    """Build a stable, concise JSON certificate of the classification."""
    triples = critical_family_triples()
    pair_counts = Counter(
        (x_family, w_family) for x_family, w_family, _ in triples
    )
    ordered_pairs = sorted(
        pair_counts,
        key=lambda pair: (family_labels(pair[0]), family_labels(pair[1])),
    )
    kk_middle_families = [
        y_family
        for x_family, w_family, y_family in triples
        if x_family == K_FAMILY and w_family == K_FAMILY
    ]

    return {
        "warning": (
            "necessary Kempe-partition relaxation only; passing families "
            "need not be realizable by actual multipoles"
        ),
        "boundary_type_counts": {
            "three_port": len(THREE_TYPES),
            "four_port": len(FOUR_TYPES),
        },
        "kempe_admissible_family_counts": {
            "three_port": len(kempe_admissible_families(3)),
            "four_port": len(kempe_admissible_families(4)),
        },
        "critical_family_triple_count": len(triples),
        "shore_family_pair_count": len(pair_counts),
        "shore_family_pairs": [
            {
                "X": family_labels(x_family),
                "W": family_labels(w_family),
                "middle_family_count": pair_counts[(x_family, w_family)],
            }
            for x_family, w_family in ordered_pairs
        ],
        "all_shores_are_R_or_K": all(
            x_family in (RAINBOW_FAMILY, K_FAMILY)
            and w_family in (RAINBOW_FAMILY, K_FAMILY)
            for x_family, w_family, _ in triples
        ),
        "K_K_middle_families": [
            family_labels(family) for family in kk_middle_families
        ],
        "minimum_deficits": {
            "R_shore": minimum_positive_deficits(RAINBOW_FAMILY),
            "K_shore": minimum_positive_deficits(K_FAMILY),
            "every_viable_middle_family_at_least": min(
                minimum_positive_deficits(y_family)
                for _, _, y_family in triples
            ),
            "all_viable_middle_families_at_least_two": all(
                minimum_positive_deficits(y_family) >= 2
                for _, _, y_family in triples
            ),
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
