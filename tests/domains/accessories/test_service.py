from datetime import datetime, timezone

from app.domains.accessories.models import AccessoryProduct
from app.domains.accessories.service import _select_recommendations


def _product(category, style_tags, occasion_tags, tone_tags, created_at) -> AccessoryProduct:
    return AccessoryProduct(
        name="Test",
        image_url="https://example.com/x.png",
        affiliate_link="https://example.com",
        category=category,
        style_tags=style_tags,
        occasion_tags=occasion_tags,
        tone_tags=tone_tags,
        is_active=True,
        created_at=created_at,
    )


def test_picks_the_highest_scoring_product_per_category():
    low = _product("tui-xach", ["casual"], [], [], datetime(2026, 1, 1, tzinfo=timezone.utc))
    high = _product("tui-xach", ["casual"], ["du-tiec"], ["winter"], datetime(2026, 1, 1, tzinfo=timezone.utc))

    result = _select_recommendations([low, high], occasion="du-tiec", style="casual", tone="winter", limit=6)

    assert result == [high]


def test_returns_at_most_one_item_per_category_for_diversity():
    bag = _product("tui-xach", ["formal"], ["du-tiec"], ["winter"], datetime(2026, 1, 1, tzinfo=timezone.utc))
    shoes = _product("giay", ["formal"], ["du-tiec"], ["winter"], datetime(2026, 1, 1, tzinfo=timezone.utc))

    result = _select_recommendations([bag, shoes], occasion="du-tiec", style="formal", tone="winter", limit=6)

    assert {item.category for item in result} == {"tui-xach", "giay"}
    assert len(result) == 2


def test_excludes_a_zero_scoring_category_while_keeping_others():
    matching_bag = _product("tui-xach", ["formal"], ["du-tiec"], ["winter"], datetime(2026, 1, 1, tzinfo=timezone.utc))
    unrelated_shoes = _product("giay", ["street"], ["hang-ngay"], ["summer"], datetime(2026, 1, 1, tzinfo=timezone.utc))

    result = _select_recommendations(
        [matching_bag, unrelated_shoes], occasion="du-tiec", style="formal", tone="winter", limit=6
    )

    assert result == [matching_bag]


def test_falls_back_to_newest_per_category_when_nothing_scores():
    older = _product("giay", ["street"], ["hang-ngay"], ["summer"], datetime(2026, 1, 1, tzinfo=timezone.utc))
    newer = _product("giay", ["street"], ["hang-ngay"], ["summer"], datetime(2026, 6, 1, tzinfo=timezone.utc))

    result = _select_recommendations([older, newer], occasion="du-tiec", style="formal", tone="winter", limit=6)

    assert result == [newer]


def test_ignores_tone_scoring_when_tone_is_none():
    product = _product("tui-xach", ["casual"], ["hang-ngay"], ["winter"], datetime(2026, 1, 1, tzinfo=timezone.utc))

    result = _select_recommendations([product], occasion="hang-ngay", style="casual", tone=None, limit=6)

    assert result == [product]


def test_scores_by_style_alone_when_occasion_is_none():
    # Tagged for a different occasion than the user ever chose — with
    # occasion=None (style-only browsing mode) it must still score purely
    # off the style match, the same way tryon job matching now works.
    matching_style = _product("tui-xach", ["formal"], ["du-tiec"], [], datetime(2026, 1, 1, tzinfo=timezone.utc))
    unrelated = _product("tui-xach", ["street"], ["hang-ngay"], [], datetime(2026, 1, 1, tzinfo=timezone.utc))

    result = _select_recommendations(
        [matching_style, unrelated], occasion=None, style="formal", tone=None, limit=6
    )

    assert result == [matching_style]


def test_scores_by_occasion_alone_when_style_is_none():
    matching_occasion = _product("giay", ["street"], ["du-tiec"], [], datetime(2026, 1, 1, tzinfo=timezone.utc))
    unrelated = _product("giay", ["formal"], ["hang-ngay"], [], datetime(2026, 1, 1, tzinfo=timezone.utc))

    result = _select_recommendations(
        [matching_occasion, unrelated], occasion="du-tiec", style=None, tone=None, limit=6
    )

    assert result == [matching_occasion]


def test_respects_the_limit_across_categories():
    bag = _product("tui-xach", ["casual"], ["hang-ngay"], [], datetime(2026, 1, 1, tzinfo=timezone.utc))
    shoes = _product("giay", ["casual"], ["hang-ngay"], [], datetime(2026, 1, 1, tzinfo=timezone.utc))
    jewelry = _product("trang-suc", ["casual"], ["hang-ngay"], [], datetime(2026, 1, 1, tzinfo=timezone.utc))

    result = _select_recommendations([bag, shoes, jewelry], occasion="hang-ngay", style="casual", tone=None, limit=2)

    assert len(result) == 2
