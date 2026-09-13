from app.domains.contact.models import ContactMessage


def test_create_contact_message_persists_expected_fields(db_session):
    message = ContactMessage(
        name="Nguyễn Văn Test",
        email="test@twistfit.vn",
        phone=None,
        subject="other",
        message="Nội dung test",
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)

    assert message.id is not None
    assert message.is_read is False
    assert message.created_at is not None


def test_contact_message_stores_an_optional_phone(db_session):
    message = ContactMessage(
        name="Nguyễn Văn Test",
        email="test@twistfit.vn",
        phone="0909123456",
        subject="stylist",
        message="Nội dung test",
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)

    assert message.phone == "0909123456"
