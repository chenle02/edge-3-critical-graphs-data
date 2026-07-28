from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import analyze_pattern_ii_boundary_states as pattern_ii


def test_restricted_growth_types_use_at_most_three_colors() -> None:
    assert len(pattern_ii.THREE_TYPES) == 5
    assert len(pattern_ii.FOUR_TYPES) == 14
    assert (0, 1, 2) in pattern_ii.THREE_TYPES
    assert (0, 1, 2, 3) not in pattern_ii.FOUR_TYPES


def test_kempe_partition_relaxation_counts_are_exact() -> None:
    assert len(pattern_ii.kempe_admissible_families(3)) == 23
    assert len(pattern_ii.kempe_admissible_families(4)) == 3767


def test_critical_family_triples_have_only_four_shore_pairs() -> None:
    triples = pattern_ii.critical_family_triples()
    pair_counts = {
        pair: sum(
            1
            for x_family, w_family, _ in triples
            if (x_family, w_family) == pair
        )
        for pair in {
            (x_family, w_family)
            for x_family, w_family, _ in triples
        }
    }

    rainbow = pattern_ii.RAINBOW_FAMILY
    k_family = pattern_ii.K_FAMILY
    assert len(triples) == 81
    assert pair_counts == {
        (rainbow, rainbow): 40,
        (rainbow, k_family): 20,
        (k_family, rainbow): 20,
        (k_family, k_family): 1,
    }


def test_k_k_case_forces_the_exact_cross_family_on_y() -> None:
    middle_families = {
        y_family
        for x_family, w_family, y_family in (
            pattern_ii.critical_family_triples()
        )
        if x_family == pattern_ii.K_FAMILY
        and w_family == pattern_ii.K_FAMILY
    }
    assert middle_families == {pattern_ii.CROSS_FAMILY}


def test_parity_forces_two_deficits_in_every_corner() -> None:
    assert pattern_ii.minimum_positive_deficits(
        pattern_ii.RAINBOW_FAMILY
    ) == 2
    assert pattern_ii.minimum_positive_deficits(pattern_ii.K_FAMILY) == 2
    assert all(
        pattern_ii.minimum_positive_deficits(y_family) >= 2
        for _, _, y_family in pattern_ii.critical_family_triples()
    )


def test_report_marks_the_result_as_only_a_necessary_relaxation() -> None:
    result = pattern_ii.report()
    assert result["critical_family_triple_count"] == 81
    assert result["shore_family_pair_count"] == 4
    assert result["all_shores_are_R_or_K"] is True
    assert (
        result["minimum_deficits"][
            "all_viable_middle_families_at_least_two"
        ]
        is True
    )
    assert "necessary" in result["warning"]
