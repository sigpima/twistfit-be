from app.domains.team.models import TeamMember
from app.domains.team.seed import seed_demo_team_members


def test_seed_demo_team_members_creates_three_members(db_session):
    seed_demo_team_members(db_session)
    members = db_session.query(TeamMember).order_by(TeamMember.id.asc()).all()
    assert len(members) == 3
    assert members[0].name == "Trần Mai Anh"
    assert members[0].badge_variant == "secondary"


def test_seed_demo_team_members_is_idempotent(db_session):
    seed_demo_team_members(db_session)
    seed_demo_team_members(db_session)
    assert db_session.query(TeamMember).count() == 3
