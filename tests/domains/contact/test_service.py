from app.domains.contact import service
from app.domains.contact.schemas import ContactMessageCreate

VALID_INPUT = ContactMessageCreate(
    name="Nguyễn Văn Test",
    email="test@twistfit.vn",
    phone=None,
    subject="other",
    message="Nội dung test",
)


def test_create_contact_message_defaults_is_read_to_false(db_session):
    created = service.create_contact_message(db_session, VALID_INPUT)
    assert created.id is not None
    assert created.is_read is False
    assert created.name == "Nguyễn Văn Test"


def test_list_contact_messages_orders_newest_first(db_session):
    service.create_contact_message(db_session, VALID_INPUT.model_copy(update={"name": "Tin 1"}))
    service.create_contact_message(db_session, VALID_INPUT.model_copy(update={"name": "Tin 2"}))
    names = [message.name for message in service.list_contact_messages(db_session)]
    assert names == ["Tin 2", "Tin 1"]


def test_get_contact_message_returns_none_when_missing(db_session):
    assert service.get_contact_message(db_session, 999999) is None


def test_set_contact_message_read_toggles_flag(db_session):
    created = service.create_contact_message(db_session, VALID_INPUT)
    marked = service.set_contact_message_read(db_session, created.id, True)
    assert marked is not None
    assert marked.is_read is True
    unmarked = service.set_contact_message_read(db_session, created.id, False)
    assert unmarked.is_read is False


def test_set_contact_message_read_returns_none_when_missing(db_session):
    assert service.set_contact_message_read(db_session, 999999, True) is None


def test_delete_contact_message_removes_it(db_session):
    created = service.create_contact_message(db_session, VALID_INPUT)
    assert service.delete_contact_message(db_session, created.id) is True
    assert service.get_contact_message(db_session, created.id) is None
    assert service.delete_contact_message(db_session, created.id) is False
