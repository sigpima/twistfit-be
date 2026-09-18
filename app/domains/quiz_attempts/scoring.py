from collections import Counter

_PARENT_SEASON_BY_QUADRANT = {
    ("warm", "bright"): "spring",
    ("warm", "muted"): "autumn",
    ("cool", "bright"): "winter",
    ("cool", "muted"): "summer",
}

_SUB_SEASON_SLOTS_BY_PARENT = {
    "spring": {"value": "light-spring", "hue": "true-spring", "chroma": "bright-spring"},
    "summer": {"value": "light-summer", "hue": "true-summer", "chroma": "soft-summer"},
    "autumn": {"value": "deep-autumn", "hue": "true-autumn", "chroma": "soft-autumn"},
    "winter": {"value": "deep-winter", "hue": "true-winter", "chroma": "bright-winter"},
}

# Official per-sub-season score bands (0-100) on each axis's universal scale
# (hue: cold->warm, value: dark->light, chroma: muted->vivid), from "Website
# Content.docx". Each axis's exact score is the vote-share confidence for the
# winning bucket, scaled into that band.
_SUB_SEASON_AXIS_SCORE_RANGES: dict[str, dict[str, tuple[int, int]]] = {
    "light-spring": {"hue": (55, 65), "value": (70, 90), "chroma": (60, 75)},
    "true-spring": {"hue": (75, 95), "value": (60, 75), "chroma": (70, 85)},
    "bright-spring": {"hue": (55, 65), "value": (65, 80), "chroma": (80, 100)},
    "light-summer": {"hue": (35, 45), "value": (70, 90), "chroma": (35, 50)},
    "true-summer": {"hue": (10, 25), "value": (55, 70), "chroma": (30, 45)},
    "soft-summer": {"hue": (35, 45), "value": (45, 60), "chroma": (15, 35)},
    "soft-autumn": {"hue": (55, 65), "value": (45, 60), "chroma": (15, 35)},
    "true-autumn": {"hue": (75, 95), "value": (40, 55), "chroma": (40, 60)},
    "deep-autumn": {"hue": (60, 70), "value": (15, 35), "chroma": (45, 60)},
    "deep-winter": {"hue": (30, 40), "value": (15, 35), "chroma": (60, 75)},
    "true-winter": {"hue": (5, 25), "value": (45, 65), "chroma": (75, 90)},
    "bright-winter": {"hue": (30, 40), "value": (60, 75), "chroma": (85, 100)},
}


def _axis_result(votes: list[str], middle_value: str) -> str:
    counts = Counter(votes)
    max_count = max(counts.values())
    winners = [value for value, count in counts.items() if count == max_count]
    return winners[0] if len(winners) == 1 else middle_value


def _axis_score(votes: list[str], axis_result: str, score_range: tuple[int, int]) -> int:
    share = votes.count(axis_result) / len(votes)
    low, high = score_range
    return round(low + share * (high - low))


def _hue_side(hue_result: str, hue_votes: list[str]) -> str:
    if hue_result != "neutral":
        return hue_result
    warm_count = hue_votes.count("warm")
    cool_count = hue_votes.count("cool")
    return "warm" if warm_count >= cool_count else "cool"


def _chroma_side(chroma_result: str, chroma_votes: list[str]) -> str:
    if chroma_result != "neutral":
        return chroma_result
    bright_count = chroma_votes.count("bright")
    muted_count = chroma_votes.count("muted")
    return "muted" if muted_count >= bright_count else "bright"


def _dominant_slot(
    value_result: str, chroma_result: str, value_votes: list[str], chroma_votes: list[str]
) -> str:
    value_share = value_votes.count(value_result) / len(value_votes) if value_result in ("dark", "light") else 0.0
    chroma_share = (
        chroma_votes.count(chroma_result) / len(chroma_votes) if chroma_result in ("bright", "muted") else 0.0
    )
    if value_share > chroma_share:
        return "value"
    if chroma_share > value_share:
        return "chroma"
    return "hue"


def score_quiz(hue_votes: list[str], value_votes: list[str], chroma_votes: list[str]) -> dict:
    hue_result = _axis_result(hue_votes, "neutral")
    value_result = _axis_result(value_votes, "medium")
    chroma_result = _axis_result(chroma_votes, "neutral")

    hue_side = _hue_side(hue_result, hue_votes)
    chroma_side = _chroma_side(chroma_result, chroma_votes)
    parent_season = _PARENT_SEASON_BY_QUADRANT[(hue_side, chroma_side)]

    dominant_slot = _dominant_slot(value_result, chroma_result, value_votes, chroma_votes)
    sub_season = _SUB_SEASON_SLOTS_BY_PARENT[parent_season][dominant_slot]
    score_ranges = _SUB_SEASON_AXIS_SCORE_RANGES[sub_season]

    return {
        "hue_result": hue_result,
        "value_result": value_result,
        "chroma_result": chroma_result,
        "parent_season": parent_season,
        "sub_season": sub_season,
        "hue_score": _axis_score(hue_votes, hue_result, score_ranges["hue"]),
        "value_score": _axis_score(value_votes, value_result, score_ranges["value"]),
        "chroma_score": _axis_score(chroma_votes, chroma_result, score_ranges["chroma"]),
    }
