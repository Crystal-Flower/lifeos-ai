from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.agents.chief_of_staff import get_ai_response, get_system_briefing
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_chief(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reply = await get_ai_response(db, current_user.id, body.message)
    return {"reply": reply}

@router.get("/daily-briefing")
def daily_briefing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    briefing = get_system_briefing(db, current_user.id)
    return {"briefing": briefing}
