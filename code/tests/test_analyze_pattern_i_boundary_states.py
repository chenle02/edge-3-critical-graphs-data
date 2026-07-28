from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import analyze_pattern_i_boundary_states as pattern_i


def test_color_orbits_relabel_colors_without_relabeling_ports() -> None:
    assert len(pattern_i.COLOR_ORBITS["M"]) == 3
    assert len(pattern_i.COLOR_ORBITS["P12"]) == 6
    assert len(pattern_i.COLOR_ORBITS["P13"]) == 6
    assert len(pattern_i.COLOR_ORBITS["P23"]) == 6
    assert len(pattern_i.COLOR_ORBITS["R"]) == 6

    assert all(
        first == second != third
        for first, second, third in pattern_i.COLOR_ORBITS["P12"]
    )


def test_full_connector_compatibility_matrix() -> None:
    compatible = {
        ("M", "P12"),
        ("M", "R"),
        ("P12", "M"),
        ("P12", "P12"),
        ("P12", "P13"),
        ("P12", "P23"),
        ("P13", "P12"),
        ("P13", "P23"),
        ("P13", "R"),
        ("P23", "P12"),
        ("P23", "P13"),
        ("P23", "R"),
        ("R", "M"),
        ("R", "P13"),
        ("R", "P23"),
        ("R", "R"),
    }
    observed = {
        (left, right)
        for left in pattern_i.TYPE_ORDER
        for right in pattern_i.TYPE_ORDER
        if pattern_i.connector_compatible(left, right)
    }
    assert observed == compatible


def test_critical_state_family_pairs_are_exactly_the_six_claimed() -> None:
    expected = {
        (frozenset({"M"}), frozenset({"P13", "P23"})),
        (frozenset({"M"}), frozenset({"M", "P13", "P23"})),
        (frozenset({"P12"}), frozenset({"R"})),
        (frozenset({"P13", "P23"}), frozenset({"M"})),
        (frozenset({"M", "P13", "P23"}), frozenset({"M"})),
        (frozenset({"R"}), frozenset({"P12"})),
    }
    assert set(pattern_i.critical_family_pairs()) == expected


def test_every_critical_pair_forces_a_kempe_forbidden_singleton() -> None:
    forbidden = {frozenset({"M"}), frozenset({"P12"})}
    assert all(
        left in forbidden or right in forbidden
        for left, right in pattern_i.critical_family_pairs()
    )
    assert pattern_i.proper_kempe_subsets_change_type("M")
    assert pattern_i.proper_kempe_subsets_change_type("P12")
