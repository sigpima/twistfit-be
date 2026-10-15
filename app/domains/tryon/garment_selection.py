from itertools import combinations

from app.domains.wardrobe.models import WardrobeItem
from app.domains.wardrobe.season_palettes import SEASON_REFERENCE_COLORS

# Cloth region CATVTON expects for each clothing-type category.
CLOTH_TYPE_BY_CATEGORY = {
    "ao": "upper",
    "ao-khoac": "upper",
    "quan": "lower",
    "vay": "lower",
    "dam": "overall",
}

# Max possible Euclidean distance between two RGB colors (black vs white).
_MAX_COLOR_DISTANCE = (255**2 * 3) ** 0.5

# Relative weights for the three compatibility axes of an outfit score.
_COLOR_WEIGHT = 0.5
_STYLE_WEIGHT = 0.3
_OCCASION_WEIGHT = 0.2

# Soft penalty subtracted from a combo's score for every past successful
# job one of its items appeared in (see service._usage_counts — only
# "done" jobs count), averaged across the combo's items. A repeat still
# wins if it's the only viable pick for its category, but a comparably-
# good alternative that hasn't been used yet will now edge it out. 9 is
# the 0-100-scale equivalent of the old 40-out-of-441 raw color distance
# penalty, so 1-2 prior uses are enough to matter without an
# already-much-better match ever losing to something merely
# less-recently used.
_USAGE_PENALTY_PER_USE = 9.0


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _color_distance(hex_a: str, hex_b: str) -> float:
    ra, ga, ba = _hex_to_rgb(hex_a)
    rb, gb, bb = _hex_to_rgb(hex_b)
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


def _color_score(item: WardrobeItem, reference_colors: list[str] | None) -> float:
    """0-100 color compatibility of an item with the user's season palette
    (100 = exact match). Neutral (50) when the season has no reference
    palette."""
    if not reference_colors:
        return 50.0
    distance = min(
        (_color_distance(c, ref) for c in item.dominant_colors for ref in reference_colors),
        default=_MAX_COLOR_DISTANCE,
    )
    return max(0.0, 100.0 - distance / _MAX_COLOR_DISTANCE * 100.0)


def _tag_overlap_score(a: WardrobeItem, b: WardrobeItem, tag: str) -> float:
    """0-100 Jaccard overlap between two items' values for a taxonomy tag
    (e.g. "style" or "occasion"). Neutral (100) if neither has the tag."""
    tags_a, tags_b = set(a.attributes.get(tag, [])), set(b.attributes.get(tag, []))
    union = tags_a | tags_b
    if not union:
        return 100.0
    return 100.0 * len(tags_a & tags_b) / len(union)


def _combo_score(combo: list[WardrobeItem], reference_colors: list[str] | None, usage_counts: dict[int, int]) -> float:
    color = sum(_color_score(item, reference_colors) for item in combo) / len(combo)

    pairs = list(combinations(combo, 2))
    if pairs:
        style = sum(_tag_overlap_score(a, b, "style") for a, b in pairs) / len(pairs)
        occasion = sum(_tag_overlap_score(a, b, "occasion") for a, b in pairs) / len(pairs)
    else:
        style = occasion = 100.0

    penalty = sum(usage_counts.get(item.id, 0) for item in combo) / len(combo) * _USAGE_PENALTY_PER_USE
    return _COLOR_WEIGHT * color + _STYLE_WEIGHT * style + _OCCASION_WEIGHT * occasion - penalty


def _clothing_category(item: WardrobeItem) -> str | None:
    types = item.attributes.get("clothing-type", [])
    return types[0] if types else None


def _group_by_category(items: list[WardrobeItem]) -> dict[str, list[WardrobeItem]]:
    groups: dict[str, list[WardrobeItem]] = {key: [] for key in CLOTH_TYPE_BY_CATEGORY}
    for item in items:
        category = _clothing_category(item)
        if category in groups:
            groups[category].append(item)
    return groups


def select_outfit_combo(
    items: list[WardrobeItem], season: str, usage_counts: dict[int, int] | None = None
) -> list[WardrobeItem] | None:
    """Pick the sequence of items to apply, in application order (an
    áo khoác, if used, is always last since it goes on top of everything
    else). The base look must be either a đầm alone, or a áo paired with
    a váy or a quần — a áo khoác is always optional on top of one of
    those, and never applied on its own or over a bare váy/quần. Returns
    None when the wardrobe can't form any such combo.

    `usage_counts` (wardrobe_item_id -> number of past successful combos
    it appeared in) softly deprioritizes items that keep getting reused —
    see _USAGE_PENALTY_PER_USE.
    """
    if not items:
        return None

    usage_counts = usage_counts or {}
    reference_colors = SEASON_REFERENCE_COLORS.get(season)
    groups = _group_by_category(items)

    base_combos: list[list[WardrobeItem]] = [[dam] for dam in groups["dam"]]
    base_combos += [[ao, vay] for ao in groups["ao"] for vay in groups["vay"]]
    base_combos += [[ao, quan] for ao in groups["ao"] for quan in groups["quan"]]

    jackets = groups["ao-khoac"]
    combos = [combo + [jacket] for combo in base_combos for jacket in jackets] if jackets else base_combos

    if not combos:
        return None

    return max(combos, key=lambda combo: _combo_score(combo, reference_colors, usage_counts))
