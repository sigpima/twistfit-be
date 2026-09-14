from app.domains.wardrobe.models import WardrobeItem
from app.domains.wardrobe.season_palettes import SEASON_REFERENCE_COLORS


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _color_distance(hex_a: str, hex_b: str) -> float:
    ra, ga, ba = _hex_to_rgb(hex_a)
    rb, gb, bb = _hex_to_rgb(hex_b)
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


def select_best_matching_item(items: list[WardrobeItem], season: str) -> WardrobeItem | None:
    if not items:
        return None

    reference_colors = SEASON_REFERENCE_COLORS.get(season)
    if not reference_colors:
        return items[0]

    def item_score(item: WardrobeItem) -> float:
        return min(
            (_color_distance(c, ref) for c in item.dominant_colors for ref in reference_colors),
            default=float("inf"),
        )

    return min(items, key=item_score)
