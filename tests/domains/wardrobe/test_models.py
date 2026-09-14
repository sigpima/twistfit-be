from app.core.security import hash_password
from app.domains.auth.models import User
from app.domains.wardrobe.models import WardrobeItem


def test_create_wardrobe_item(db_session):
    user = User(name="Test", email="wardrobe-model@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    item = WardrobeItem(
        user_id=user.id,
        blob_url="https://example.com/wardrobe/1.png",
        category="ao-thun",
        style_tags=["casual"],
        occasion_tags=["hang-ngay"],
        dominant_colors=["#ff0000"],
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    assert item.id is not None
    assert item.user_id == user.id
    assert item.style_tags == ["casual"]
