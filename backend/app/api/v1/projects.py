from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Project, Milestone
from app.schemas.schemas import ProjectResponse, ProjectCreate, ProjectUpdate, MilestoneResponse, MilestoneCreate, MilestoneUpdate

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Project).filter(Project.userId == current_user.id).all()

@router.post("/", response_model=ProjectResponse)
def create_project(
    body: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = Project(**body.model_dump(), userId=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    body: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.userId == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    for var, value in body.model_dump(exclude_unset=True).items():
        setattr(project, var, value)
        
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.userId == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}

@router.get("/{project_id}/milestones", response_model=List[MilestoneResponse])
def get_milestones(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.userId == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(Milestone).filter(Milestone.projectId == project_id).all()

@router.post("/{project_id}/milestones", response_model=MilestoneResponse)
def create_milestone(
    project_id: str,
    body: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.userId == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    milestone = Milestone(**body.model_dump(), projectId=project_id)
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone

@router.put("/milestones/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: str,
    body: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    milestone = db.query(Milestone).join(Project).filter(
        Milestone.id == milestone_id, Project.userId == current_user.id
    ).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
        
    for var, value in body.model_dump(exclude_unset=True).items():
        setattr(milestone, var, value)
        
    db.commit()
    db.refresh(milestone)
    
    project = milestone.project
    all_milestones = db.query(Milestone).filter(Milestone.projectId == project.id).all()
    if all_milestones:
        completed = sum(1 for m in all_milestones if m.isCompleted)
        project.progress = float(completed) / len(all_milestones) * 100.0
        db.commit()
        
    return milestone
