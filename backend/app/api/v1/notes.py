from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import openai
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Note
from app.schemas.schemas import NoteResponse, NoteCreate, NoteUpdate
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[NoteResponse])
def get_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Note).filter(Note.userId == current_user.id).all()

@router.post("/", response_model=NoteResponse)
def create_note(
    body: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = Note(**body.model_dump(), userId=current_user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    body: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.userId == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    for var, value in body.model_dump(exclude_unset=True).items():
        setattr(note, var, value)
        
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}")
def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.userId == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"detail": "Note deleted"}

@router.post("/{note_id}/summarize", response_model=NoteResponse)
def summarize_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(Note.id == note_id, Note.userId == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    summary = note.content[:100] + "..." if len(note.content) > 100 else note.content
    
    if settings.OPENAI_API_KEY:
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = f"Summarize the following note in 1 or 2 concise sentences:\n\n{note.content}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            summary = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI for summary: {e}")
            
    note.summary = summary
    db.commit()
    db.refresh(note)
    return note
