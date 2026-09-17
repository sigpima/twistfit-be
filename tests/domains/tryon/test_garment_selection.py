from app.domains.tryon.garment_selection import select_best_matching_item
from app.domains.wardrobe.models import WardrobeItem


def _item(colors: list[str]) -> WardrobeItem:
    return WardrobeItem(
        user_id=1,
        blob_url="https://example.com/x.png",
        attributes={"clothing-type": ["ao"], "style": ["casual"], "occasion": ["hang-ngay"]},
        dominant_colors=colors,
    )


def test_picks_the_item_closest_to_the_season_palette():
    orange_item = _item(["#F2A93B"])  # an exact spring-warm color
    navy_item = _item(["#000080"])  # far from every spring color

    best = select_best_matching_item([navy_item, orange_item], "spring")

    assert best is orange_item


def test_returns_none_for_an_empty_list():
    assert select_best_matching_item([], "spring") is None


def test_falls_back_to_the_first_item_for_an_unknown_season():
    item = _item(["#ffffff"])
    assert select_best_matching_item([item], "not-a-season") is item
