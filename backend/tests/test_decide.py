"""The decision rules, vote and photo messages on made-up numbers. Fast; no model files needed."""

import pytest

from app.predict import GENERIC_TIP, PHOTO_TIPS, decide, photo_message, unique_neighbours, weighted_vote

# The Day 2 cut-offs (backend/models/thresholds.json, made 19 Nov 2026)
T = {"sure": 0.90235, "not_sure": 0.60135, "not_a_leaf": 0.76018, "photo_check_sure": 0.6}


@pytest.mark.parametrize("kind, share, best, level, level_sure, expected", [
    # 1. not a leaf beats everything
    ("disease", 1.0, 0.70, "L0", 1.0, ("retake", "not_a_leaf")),
    ("healthy", 1.0, 0.70, "L0", 1.0, ("retake", "not_a_leaf")),
    # 2. the photo check is sure it is L3 and the vote is weak -> retake
    ("disease", 0.50, 0.90, "L3", 0.90, ("retake", "too_unclear")),
    ("healthy", 0.50, 0.90, "L3", 0.90, ("retake", "too_unclear")),
    # ... but not when the photo check itself is unsure about L3
    ("disease", 0.50, 0.90, "L3", 0.50, ("not_sure", "weak_vote")),
    # 3. healthy / look-alike: only with a very strong vote and not L3 (option C)
    ("healthy", 1.00, 0.90, "L0", 0.90, ("healthy", None)),
    ("healthy", 0.95, 0.90, "L2", 0.90, ("healthy", None)),
    ("other", 1.00, 0.90, "L1", 0.90, ("not_in_list", None)),
    ("healthy", 1.00, 0.90, "L3", 0.90, ("not_sure", "healthy_or_other_unclear")),
    ("healthy", 1.00, 0.90, "L3", 0.40, ("not_sure", "healthy_or_other_unclear")),
    ("other", 0.80, 0.90, "L0", 0.90, ("not_sure", "healthy_or_other_unclear")),
    ("healthy", 0.65, 0.90, "L3", 0.90, ("not_sure", "healthy_or_other_unclear")),
    # 4. our 8 diseases
    ("disease", 1.00, 0.90, "L0", 0.90, ("sure", None)),
    ("disease", 0.95, 0.90, "L3", 0.90, ("sure", None)),
    ("disease", 0.80, 0.90, "L1", 0.90, ("likely", None)),
    ("disease", 0.50, 0.90, "L1", 0.90, ("not_sure", "weak_vote")),
])
def test_decision_rules(kind, share, best, level, level_sure, expected):
    assert decide(kind, share, best, level, level_sure, T) == expected


def test_cut_offs_count_as_reached():
    assert decide("disease", T["sure"], 0.9, "L0", 1.0, T)[0] == "sure"
    assert decide("disease", T["not_sure"], 0.9, "L0", 1.0, T)[0] == "likely"
    assert decide("healthy", T["sure"], 0.9, "L2", 1.0, T)[0] == "healthy"
    assert decide("disease", 1.0, T["not_a_leaf"], "L0", 1.0, T)[0] == "sure"


def test_weighted_vote_adds_similarities_per_label():
    ranked = weighted_vote(["a", "a", "b", "a", "b"], [0.9, 0.8, 0.85, 0.7, 0.6])
    assert [lab for lab, _ in ranked] == ["a", "b"]
    assert ranked[0][1] == pytest.approx(2.4 / 3.85, abs=1e-5)
    assert sum(s for _, s in ranked) == pytest.approx(1.0)


def test_weighted_vote_ignores_negative_similarity():
    ranked = weighted_vote(["a", "b"], [0.5, -0.3])
    assert ranked[0] == ("a", pytest.approx(1.0, abs=1e-5))


def test_neighbours_skip_copies_of_the_same_photo():
    class FakeLibrary:
        photo_id = ["p1", "p1", "p2", "p1", "p3", "p4", "p2", "p5", "p6"]

    assert unique_neighbours(range(9), FakeLibrary(), n=5) == [0, 2, 4, 5, 7]


def test_photo_messages():
    assert photo_message({"problem": "clean", "level": "L0"}) is None
    assert photo_message({"problem": "motion_blur", "level": "L0"}) is None  # L0: nothing to warn about
    blurry = photo_message({"problem": "motion_blur", "level": "L2"})
    assert blurry == photo_message({"problem": "defocus_blur", "level": "L3"})  # one "blurry" message for both
    assert "blurry" in blurry
    assert photo_message({"problem": "low_light", "level": "L1"}) == PHOTO_TIPS["low_light"]
    assert photo_message({"problem": "something_new", "level": "L2"}) == GENERIC_TIP
