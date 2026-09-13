import pytest
from pydantic import ValidationError

from app.domains.team import service
from app.domains.team.schemas import TeamMemberInput

VALID_INPUT = {
    "image": "/about/a.jpg",
    "name": "Nguyễn Văn A",
    "role": "Stylist",
    "bio": "Tiểu sử mẫu.",
    "badgeVariant": "primary",
    "roleVariant": "primary",
    "footerIcon": "star",
    "footerLabel": "Nhãn mẫu",
}


def test_create_team_member(db_session):
    member = service.create_team_member(db_session, TeamMemberInput(**VALID_INPUT))
    assert member.id is not None
    assert member.name == "Nguyễn Văn A"


def test_list_team_members_orders_by_id(db_session):
    first = service.create_team_member(db_session, TeamMemberInput(**VALID_INPUT))
    second = service.create_team_member(db_session, TeamMemberInput(**{**VALID_INPUT, "name": "B"}))
    members = service.list_team_members(db_session)
    assert [m.id for m in members] == [first.id, second.id]


def test_get_team_member_returns_none_when_missing(db_session):
    assert service.get_team_member(db_session, 99999) is None


def test_update_team_member(db_session):
    member = service.create_team_member(db_session, TeamMemberInput(**VALID_INPUT))
    updated = service.update_team_member(db_session, member.id, TeamMemberInput(**{**VALID_INPUT, "name": "Đã sửa"}))
    assert updated is not None
    assert updated.name == "Đã sửa"


def test_update_team_member_returns_none_when_missing(db_session):
    assert service.update_team_member(db_session, 99999, TeamMemberInput(**VALID_INPUT)) is None


def test_delete_team_member(db_session):
    member = service.create_team_member(db_session, TeamMemberInput(**VALID_INPUT))
    assert service.delete_team_member(db_session, member.id) is True
    assert service.get_team_member(db_session, member.id) is None


def test_delete_team_member_returns_false_when_missing(db_session):
    assert service.delete_team_member(db_session, 99999) is False


def test_team_member_input_rejects_blank_name():
    with pytest.raises(ValidationError):
        TeamMemberInput(**{**VALID_INPUT, "name": "   "})


def test_team_member_input_rejects_invalid_badge_variant():
    with pytest.raises(ValidationError):
        TeamMemberInput(**{**VALID_INPUT, "badgeVariant": "not-a-real-variant"})
