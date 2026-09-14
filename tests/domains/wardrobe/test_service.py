from app.domains.auth import service as auth_service
from app.domains.wardrobe import service
from app.domains.wardrobe.schemas import WardrobeItemCreate


def test_create_and_list_items_for_a_user(db_session):
    user = auth_service.create_user(db_session, name="Test", email="wardrobe-svc@example.com", password="password123")
    other_user = auth_service.create_user(db_session, name="Other", email="wardrobe-svc-2@example.com", password="password123")

    service.create_item(
        db_session,
        user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/a.png",
            category="ao-thun",
            style_tags=["casual"],
            occasion_tags=["hang-ngay"],
            dominant_colors=["#ff0000"],
        ),
    )
    service.create_item(
        db_session,
        other_user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/b.png",
            category="dam",
            style_tags=["formal"],
            occasion_tags=["du-tiec"],
            dominant_colors=["#0000ff"],
        ),
    )

    items = service.list_items(db_session, user.id)

    assert len(items) == 1
    assert items[0].category == "ao-thun"


def test_get_item_returns_none_for_another_users_item(db_session):
    user = auth_service.create_user(db_session, name="Test", email="wardrobe-svc-3@example.com", password="password123")
    other_user = auth_service.create_user(db_session, name="Other", email="wardrobe-svc-4@example.com", password="password123")
    item = service.create_item(
        db_session,
        other_user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/c.png",
            category="quan-jean",
            style_tags=["street"],
            occasion_tags=["hang-ngay"],
            dominant_colors=["#111111"],
        ),
    )

    assert service.get_item(db_session, user.id, item.id) is None
