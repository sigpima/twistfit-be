from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.domains.team import service
from app.domains.team.schemas import TeamMemberInput, TeamMemberResponse

router = APIRouter(prefix="/team", tags=["team"])


@router.get("", response_model=list[TeamMemberResponse])
def list_items(db: Session = Depends(get_db)):
    return service.list_team_members(db)


@router.get("/{member_id}", response_model=TeamMemberResponse)
def get_item(member_id: int, db: Session = Depends(get_db)):
    member = service.get_team_member(db, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thành viên")
    return member


@router.post("", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
def create_item(body: TeamMemberInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return service.create_team_member(db, body)


@router.put("/{member_id}", response_model=TeamMemberResponse)
def update_item(member_id: int, body: TeamMemberInput, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    updated = service.update_team_member(db, member_id, body)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thành viên")
    return updated


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(member_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    deleted = service.delete_team_member(db, member_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thành viên")
