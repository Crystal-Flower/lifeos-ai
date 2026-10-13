from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Task, Reminder
from app.schemas.schemas import TaskResponse, TaskCreate, TaskUpdate
from app.services.nlp_parser import parse_task_ai
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class QuickParseRequest(BaseModel):
    text: str

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    projectId: Optional[str] = None,
    competitionId: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Task).filter(Task.userId == current_user.id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if projectId:
        query = query.filter(Task.projectId == projectId)
    if competitionId:
        query = query.filter(Task.competitionId == competitionId)
    return query.all()

@router.post("/", response_model=TaskResponse)
def create_task(
    body: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = Task(**body.model_dump(), userId=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.post("/quick-parse", response_model=TaskResponse)
async def quick_parse_task(
    body: QuickParseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parsed = await parse_task_ai(body.text)
    task = Task(**parsed, userId=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.post("/test-reminder")
def create_test_reminder(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = Task(
        userId=current_user.id,
        title="Test Real-Time Notification!",
        description="Verify that the background worker and WebSocket trigger notifications instantly.",
        status="TODO",
        priority="URGENT",
        estimatedMinutes=5
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    reminder = Reminder(
        userId=current_user.id,
        taskId=task.id,
        scheduledTime=datetime.utcnow() + timedelta(seconds=5),
        channel="BROWSER",
        urgencyLevel="URGENT",
        status="PENDING"
    )
    db.add(reminder)
    db.commit()
    
    return {"status": "success", "detail": "Test reminder scheduled to fire in 5 seconds."}

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.userId == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    for var, value in body.model_dump(exclude_unset=True).items():
        setattr(task, var, value)
        
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.userId == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}
