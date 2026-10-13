from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.ai_scheduler import run_ai_scheduler

router = APIRouter()

@router.post("/auto-schedule")
def auto_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = run_ai_scheduler(db, current_user.id)
    return result
