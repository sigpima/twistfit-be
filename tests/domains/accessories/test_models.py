from app.domains.accessories.models import AccessoryProduct


def test_create_accessory_product(db_session):
    product = AccessoryProduct(
        name="Túi tote nâu",
        image_url="https://example.com/tote.png",
        affiliate_link="https://shop.example.com/tote",
        category="tui-xach",
        style_tags=["casual"],
        occasion_tags=["hang-ngay"],
        tone_tags=["autumn"],
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    assert product.id is not None
    assert product.is_active is True
    assert product.category == "tui-xach"
    assert product.tone_tags == ["autumn"]
