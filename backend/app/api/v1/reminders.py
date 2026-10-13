from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Reminder
from pydantic import BaseModel

router = APIRouter()

class SnoozeRequest(BaseModel):
    minutes: int = 5

@router.post("/{reminder_id}/snooze")
def snooze_reminder(
    reminder_id: str,
    body: SnoozeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.userId == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
        
    reminder.status = "PENDING"
    reminder.scheduledTime = datetime.utcnow() + timedelta(minutes=body.minutes)
    reminder.snoozeCount += 1
    
    db.commit()
    db.refresh(reminder)
    
    print(f"Snoozed reminder {reminder.id} by {body.minutes} minutes. Snooze count: {reminder.snoozeCount}")
    return {"status": "success", "message": f"Reminder snoozed for {body.minutes} minutes."}
