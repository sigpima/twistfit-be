from sqlalchemy.orm import Session

from app.domains.team.models import TeamMember
from app.domains.team.schemas import TeamMemberInput


def list_team_members(db: Session) -> list[TeamMember]:
    return db.query(TeamMember).order_by(TeamMember.id.asc()).all()


def get_team_member(db: Session, member_id: int) -> TeamMember | None:
    return db.get(TeamMember, member_id)


def create_team_member(db: Session, data: TeamMemberInput) -> TeamMember:
    member = TeamMember(**data.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_team_member(db: Session, member_id: int, data: TeamMemberInput) -> TeamMember | None:
    member = get_team_member(db, member_id)
    if member is None:
        return None
    for field, value in data.model_dump().items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member


def delete_team_member(db: Session, member_id: int) -> bool:
    member = get_team_member(db, member_id)
    if member is None:
        return False
    db.delete(member)
    db.commit()
    return True
