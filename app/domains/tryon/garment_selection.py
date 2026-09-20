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


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _color_distance(hex_a: str, hex_b: str) -> float:
    ra, ga, ba = _hex_to_rgb(hex_a)
    rb, gb, bb = _hex_to_rgb(hex_b)
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


def _item_score(item: WardrobeItem, reference_colors: list[str]) -> float:
    return min(
        (_color_distance(c, ref) for c in item.dominant_colors for ref in reference_colors),
        default=float("inf"),
    )


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


def select_outfit_combo(items: list[WardrobeItem], season: str) -> list[WardrobeItem] | None:
    """Pick the sequence of items to apply, in application order (an
    áo khoác, if used, is always last since it goes on top of everything
    else). The base look must be either a đầm alone, or a áo paired with
    a váy or a quần — a áo khoác is always optional on top of one of
    those, and never applied on its own or over a bare váy/quần. Returns
    None when the wardrobe can't form any such combo.
    """
    if not items:
        return None

    reference_colors = SEASON_REFERENCE_COLORS.get(season)
    groups = _group_by_category(items)

    def best(category: str) -> WardrobeItem | None:
        candidates = groups[category]
        if not candidates:
            return None
        if not reference_colors:
            return candidates[0]
        return min(candidates, key=lambda item: _item_score(item, reference_colors))

    def score_of(item: WardrobeItem) -> float:
        if not reference_colors:
            return 0.0
        return _item_score(item, reference_colors)

    base_combos: list[list[WardrobeItem]] = []

    dam = best("dam")
    if dam is not None:
        base_combos.append([dam])

    ao = best("ao")
    vay = best("vay")
    if ao is not None and vay is not None:
        base_combos.append([ao, vay])

    quan = best("quan")
    if ao is not None and quan is not None:
        base_combos.append([ao, quan])

    jacket = best("ao-khoac")
    combos = [combo + [jacket] for combo in base_combos] if jacket is not None else base_combos

    if not combos:
        return None

    return min(combos, key=lambda combo: sum(score_of(item) for item in combo) / len(combo))
