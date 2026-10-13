from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Competition, TeamMember
from app.schemas.schemas import CompetitionResponse, CompetitionCreate, CompetitionUpdate, TeamMemberResponse, TeamMemberCreate

router = APIRouter()

@router.get("/", response_model=List[CompetitionResponse])
def get_competitions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Competition).filter(Competition.userId == current_user.id).all()

@router.post("/", response_model=CompetitionResponse)
def create_competition(
    body: CompetitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comp = Competition(**body.model_dump(), userId=current_user.id)
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp

@router.put("/{comp_id}", response_model=CompetitionResponse)
def update_competition(
    comp_id: str,
    body: CompetitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comp = db.query(Competition).filter(Competition.id == comp_id, Competition.userId == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    for var, value in body.model_dump(exclude_unset=True).items():
        setattr(comp, var, value)
        
    progress = 0.0
    if comp.reportSubmitted: progress += 25.0
    if comp.pptSubmitted: progress += 25.0
    if comp.demoLink: progress += 25.0
    if comp.githubUrl: progress += 25.0
    comp.progress = progress
    
    db.commit()
    db.refresh(comp)
    return comp

@router.delete("/{comp_id}")
def delete_competition(
    comp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comp = db.query(Competition).filter(Competition.id == comp_id, Competition.userId == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    db.delete(comp)
    db.commit()
    return {"detail": "Competition deleted"}

@router.get("/{comp_id}/members", response_model=List[TeamMemberResponse])
def get_team_members(
    comp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comp = db.query(Competition).filter(Competition.id == comp_id, Competition.userId == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    return db.query(TeamMember).filter(TeamMember.competitionId == comp_id).all()

@router.post("/{comp_id}/members", response_model=TeamMemberResponse)
def add_team_member(
    comp_id: str,
    body: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comp = db.query(Competition).filter(Competition.id == comp_id, Competition.userId == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
        
    member = TeamMember(**body.model_dump(), competitionId=comp_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

@router.delete("/members/{member_id}")
def remove_team_member(
    member_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    member = db.query(TeamMember).join(Competition).filter(
        TeamMember.id == member_id, Competition.userId == current_user.id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Team member not found")
    db.delete(member)
    db.commit()
    return {"detail": "Team member removed"}
