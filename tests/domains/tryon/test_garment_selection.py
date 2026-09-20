from app.domains.tryon.garment_selection import select_outfit_combo
from app.domains.wardrobe.models import WardrobeItem


def _item(category: str, colors: list[str]) -> WardrobeItem:
    return WardrobeItem(
        user_id=1,
        blob_url=f"https://example.com/{category}.png",
        attributes={"clothing-type": [category], "style": ["casual"], "occasion": ["hang-ngay"]},
        dominant_colors=colors,
    )


def test_returns_none_for_an_empty_list():
    assert select_outfit_combo([], "spring") is None


def test_a_dress_alone_is_a_complete_combo():
    dress = _item("dam", ["#F2A93B"])
    assert select_outfit_combo([dress], "spring") == [dress]


def test_a_skirt_alone_is_not_a_complete_combo():
    skirt = _item("vay", ["#F2A93B"])
    assert select_outfit_combo([skirt], "spring") is None


def test_a_shirt_alone_is_not_a_complete_combo():
    shirt = _item("ao", ["#F2A93B"])
    assert select_outfit_combo([shirt], "spring") is None


def test_pants_alone_are_not_a_complete_combo():
    pants = _item("quan", ["#F2A93B"])
    assert select_outfit_combo([pants], "spring") is None


def test_a_jacket_alone_is_not_a_complete_combo():
    jacket = _item("ao-khoac", ["#F2A93B"])
    assert select_outfit_combo([jacket], "spring") is None


def test_shirt_and_pants_combine_shirt_first_then_pants():
    shirt = _item("ao", ["#F2A93B"])
    pants = _item("quan", ["#F2A93B"])
    assert select_outfit_combo([shirt, pants], "spring") == [shirt, pants]


def test_shirt_and_skirt_combine_shirt_first_then_skirt():
    shirt = _item("ao", ["#F2A93B"])
    skirt = _item("vay", ["#F2A93B"])
    assert select_outfit_combo([shirt, skirt], "spring") == [shirt, skirt]


def test_jacket_with_only_a_skirt_and_no_shirt_is_not_a_complete_combo():
    skirt = _item("vay", ["#F2A93B"])
    jacket = _item("ao-khoac", ["#F2A93B"])
    assert select_outfit_combo([skirt, jacket], "spring") is None


def test_jacket_is_always_applied_last_over_a_dress():
    dress = _item("dam", ["#F2A93B"])
    jacket = _item("ao-khoac", ["#F2A93B"])
    assert select_outfit_combo([dress, jacket], "spring") == [dress, jacket]


def test_jacket_is_always_applied_last_over_shirt_and_pants():
    shirt = _item("ao", ["#F2A93B"])
    pants = _item("quan", ["#F2A93B"])
    jacket = _item("ao-khoac", ["#F2A93B"])
    assert select_outfit_combo([shirt, pants, jacket], "spring") == [shirt, pants, jacket]


def test_jacket_with_only_a_shirt_and_no_pants_is_not_a_complete_combo():
    shirt = _item("ao", ["#F2A93B"])
    jacket = _item("ao-khoac", ["#F2A93B"])
    assert select_outfit_combo([shirt, jacket], "spring") is None


def test_prefers_the_combo_with_the_best_average_color_score():
    # An exact spring-warm color vs colors far from every spring reference.
    good_dress = _item("dam", ["#F2A93B"])
    bad_shirt = _item("ao", ["#000080"])
    bad_pants = _item("quan", ["#000080"])

    result = select_outfit_combo([good_dress, bad_shirt, bad_pants], "spring")

    assert result == [good_dress]


def test_prefers_shirt_and_skirt_over_shirt_and_pants_when_the_skirt_scores_better():
    shirt = _item("ao", ["#F2A93B"])
    good_skirt = _item("vay", ["#F2A93B"])
    bad_pants = _item("quan", ["#000080"])

    result = select_outfit_combo([shirt, good_skirt, bad_pants], "spring")

    assert result == [shirt, good_skirt]


def test_picks_the_best_item_within_a_category_when_several_match():
    close_shirt = _item("ao", ["#F2A93B"])
    far_shirt = _item("ao", ["#000080"])
    pants = _item("quan", ["#F2A93B"])

    result = select_outfit_combo([far_shirt, close_shirt, pants], "spring")

    assert result == [close_shirt, pants]


def test_falls_back_to_the_first_item_per_category_for_an_unknown_season():
    dress = _item("dam", ["#ffffff"])
    assert select_outfit_combo([dress], "not-a-season") == [dress]
