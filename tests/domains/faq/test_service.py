import pytest
from pydantic import ValidationError

from app.domains.faq import service
from app.domains.faq.schemas import FaqItemInput

VALID_INPUT = {
    "categories": ["account"],
    "question": "Câu hỏi mẫu?",
    "answerMarkdown": "Trả lời mẫu.",
    "highlightIcon": "info",
    "highlightText": "Ghi chú.",
}


def test_create_faq_item(db_session):
    item = service.create_faq_item(db_session, FaqItemInput(**VALID_INPUT))
    assert item.id is not None
    assert item.question == "Câu hỏi mẫu?"
    assert item.categories == ["account"]


def test_list_faq_items_orders_by_id(db_session):
    first = service.create_faq_item(db_session, FaqItemInput(**VALID_INPUT))
    second = service.create_faq_item(db_session, FaqItemInput(**{**VALID_INPUT, "question": "Câu hỏi 2?"}))
    items = service.list_faq_items(db_session)
    assert [item.id for item in items] == [first.id, second.id]


def test_get_faq_item_returns_none_when_missing(db_session):
    assert service.get_faq_item(db_session, 99999) is None


def test_update_faq_item(db_session):
    item = service.create_faq_item(db_session, FaqItemInput(**VALID_INPUT))
    updated = service.update_faq_item(
        db_session, item.id, FaqItemInput(**{**VALID_INPUT, "question": "Câu hỏi đã sửa?"})
    )
    assert updated is not None
    assert updated.question == "Câu hỏi đã sửa?"


def test_update_faq_item_returns_none_when_missing(db_session):
    assert service.update_faq_item(db_session, 99999, FaqItemInput(**VALID_INPUT)) is None


def test_delete_faq_item(db_session):
    item = service.create_faq_item(db_session, FaqItemInput(**VALID_INPUT))
    assert service.delete_faq_item(db_session, item.id) is True
    assert service.get_faq_item(db_session, item.id) is None


def test_delete_faq_item_returns_false_when_missing(db_session):
    assert service.delete_faq_item(db_session, 99999) is False


def test_faq_item_input_rejects_blank_question():
    with pytest.raises(ValidationError):
        FaqItemInput(**{**VALID_INPUT, "question": "   "})


def test_faq_item_input_rejects_empty_categories():
    with pytest.raises(ValidationError):
        FaqItemInput(**{**VALID_INPUT, "categories": []})


def test_faq_item_input_rejects_invalid_highlight_icon():
    with pytest.raises(ValidationError):
        FaqItemInput(**{**VALID_INPUT, "highlightIcon": "not-a-real-icon"})
