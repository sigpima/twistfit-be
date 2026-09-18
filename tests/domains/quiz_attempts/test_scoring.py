import pytest

from app.domains.quiz_attempts.scoring import score_quiz


def test_clear_hue_and_chroma_majority_picks_the_parent_season():
    result = score_quiz(
        hue_votes=["warm", "warm", "warm", "warm", "cool"],
        value_votes=["light", "light", "medium"],
        chroma_votes=["bright", "bright"],
    )
    assert result["hue_result"] == "warm"
    assert result["chroma_result"] == "bright"
    assert result["parent_season"] == "spring"


@pytest.mark.parametrize(
    "hue,chroma,expected_parent",
    [
        ("warm", "bright", "spring"),
        ("warm", "muted", "autumn"),
        ("cool", "bright", "winter"),
        ("cool", "muted", "summer"),
    ],
)
def test_all_four_hue_chroma_quadrants(hue, chroma, expected_parent):
    hue_votes = [hue] * 5
    chroma_votes = [chroma] * 2
    result = score_quiz(hue_votes, ["medium", "medium", "medium"], chroma_votes)
    assert result["parent_season"] == expected_parent


def test_hue_axis_tie_falls_back_to_neutral():
    # 2 warm / 2 cool / 1 neutral: no single max -> neutral
    result = score_quiz(
        hue_votes=["warm", "warm", "cool", "cool", "neutral"],
        value_votes=["medium", "medium", "medium"],
        chroma_votes=["neutral", "neutral"],
    )
    assert result["hue_result"] == "neutral"


def test_neutral_hue_result_falls_back_to_raw_warm_vs_cool_lean():
    # hue tie -> "neutral", but raw count leans warm 3 vs cool 1 (1 neutral vote)
    result = score_quiz(
        hue_votes=["warm", "warm", "cool", "cool", "neutral"],
        value_votes=["medium", "medium", "medium"],
        chroma_votes=["bright", "bright"],
    )
    # tie is 2-2-1 among warm/cool/neutral -> axis result is neutral (no single max)
    assert result["hue_result"] == "neutral"
    # but raw warm(2) == cool(2) here too, so this case is a full deadlock -> defaults to warm
    assert result["parent_season"] == "spring"


def test_neutral_hue_result_with_a_real_secondary_lean_picks_that_side():
    result = score_quiz(
        hue_votes=["warm", "warm", "warm", "cool", "neutral"],
        value_votes=["medium", "medium", "medium"],
        chroma_votes=["bright", "bright"],
    )
    # 3 warm / 1 cool / 1 neutral -> single max is warm (3), so hue_result is "warm" outright
    assert result["hue_result"] == "warm"
    assert result["parent_season"] == "spring"


def test_chroma_axis_full_tie_falls_back_to_muted_default():
    result = score_quiz(
        hue_votes=["cool", "cool", "cool", "cool", "cool"],
        value_votes=["medium", "medium", "medium"],
        chroma_votes=["bright", "muted"],
    )
    assert result["chroma_result"] == "neutral"
    assert result["parent_season"] == "summer"


def test_axis_scores_are_scaled_into_the_winning_sub_seasons_official_band():
    # hue: cool 4/5 (share .8); value: light/dark tie -> "medium" fallback (share 0);
    # chroma: bright 3/3 (share 1.0) -> parent_season=winter, sub_season=bright-winter
    # (chroma-dominant slot). Official bands for bright-winter: hue (30,40),
    # value (60,75), chroma (85,100).
    result = score_quiz(
        hue_votes=["cool", "cool", "warm", "cool", "cool"],
        value_votes=["light", "dark"],
        chroma_votes=["bright", "bright", "bright"],
    )
    assert result["sub_season"] == "bright-winter"
    assert result["hue_score"] == 38  # 30 + .8 * (40-30)
    assert result["value_score"] == 60  # 60 + 0 * (75-60)
    assert result["chroma_score"] == 100  # 85 + 1.0 * (100-85)


def test_value_dominant_sub_season():
    # value is unanimous (3/3 = 1.0 share); chroma landed on neutral (share 0)
    result = score_quiz(
        hue_votes=["warm", "warm", "warm", "warm", "warm"],
        value_votes=["light", "light", "light"],
        chroma_votes=["bright", "neutral"],
    )
    assert result["parent_season"] == "spring"
    assert result["sub_season"] == "light-spring"


def test_chroma_dominant_sub_season():
    # chroma unanimous (2/2 = 1.0); value landed on medium (share 0)
    result = score_quiz(
        hue_votes=["warm", "warm", "warm", "warm", "warm"],
        value_votes=["medium", "medium", "light"],
        chroma_votes=["bright", "bright"],
    )
    assert result["parent_season"] == "spring"
    assert result["sub_season"] == "bright-spring"


def test_equal_shares_default_to_true_sub_season():
    # Both value and chroma land on their middle value -> both shares are 0 (a tie)
    # -> falls to the hue-dominant "true-*" slot. chroma_votes tie 1-1 -> "neutral"
    # axis result, and its side-fallback (muted_count >= bright_count, 1 >= 1) picks
    # "muted" for the parent-season quadrant -> cool + muted -> summer.
    result = score_quiz(
        hue_votes=["cool", "cool", "cool", "cool", "cool"],
        value_votes=["medium", "medium", "medium"],
        chroma_votes=["bright", "muted"],
    )
    assert result["parent_season"] == "summer"
    assert result["sub_season"] == "true-summer"


@pytest.mark.parametrize(
    "parent_hue,parent_chroma,value_votes,chroma_votes,expected_sub_season",
    [
        # Summer: value-dominant -> light-summer, chroma-dominant -> soft-summer
        ("cool", "muted", ["light", "light", "light"], ["muted", "neutral"], "light-summer"),
        ("cool", "muted", ["medium", "medium", "light"], ["muted", "muted"], "soft-summer"),
        # Autumn: value-dominant -> deep-autumn, chroma-dominant -> soft-autumn
        ("warm", "muted", ["dark", "dark", "dark"], ["muted", "neutral"], "deep-autumn"),
        ("warm", "muted", ["medium", "medium", "dark"], ["muted", "muted"], "soft-autumn"),
        # Winter: value-dominant -> deep-winter, chroma-dominant -> bright-winter
        ("cool", "bright", ["dark", "dark", "dark"], ["bright", "neutral"], "deep-winter"),
        ("cool", "bright", ["medium", "medium", "dark"], ["bright", "bright"], "bright-winter"),
    ],
)
def test_sub_season_dominance_across_all_parent_seasons(
    parent_hue, parent_chroma, value_votes, chroma_votes, expected_sub_season
):
    result = score_quiz(
        hue_votes=[parent_hue] * 5,
        value_votes=value_votes,
        chroma_votes=chroma_votes,
    )
    assert result["sub_season"] == expected_sub_season
