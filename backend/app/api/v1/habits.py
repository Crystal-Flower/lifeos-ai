from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Habit, HabitLog
from app.schemas.schemas import HabitResponse, HabitCreate, HabitUpdate, HabitLogResponse

router = APIRouter()

@router.get("/", response_model=List[HabitResponse])
def get_habits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Habit).filter(Habit.userId == current_user.id).all()

@router.post("/", response_model=HabitResponse)
def create_habit(
    body: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = Habit(**body.model_dump(), userId=current_user.id)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit

@router.post("/{habit_id}/log", response_model=HabitLogResponse)
def log_habit(
    habit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.userId == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    today = datetime.utcnow().date()
    existing_log = db.query(HabitLog).filter(
        HabitLog.habitId == habit_id,
        HabitLog.date >= datetime(today.year, today.month, today.day),
        HabitLog.date < datetime(today.year, today.month, today.day) + timedelta(days=1)
    ).first()
    
    if existing_log:
        return existing_log
        
    log = HabitLog(habitId=habit_id, completed=True)
    db.add(log)
    
    habit.streak += 1
    
    db.commit()
    db.refresh(log)
    db.refresh(habit)
    return log

@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: str,
    body: HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.userId == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
        
    for var, value in body.model_dump(exclude_unset=True).items():
        setattr(habit, var, value)
        
    db.commit()
    db.refresh(habit)
    return habit

@router.delete("/{habit_id}")
def delete_habit(
    habit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.userId == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()
    return {"detail": "Habit deleted"}
