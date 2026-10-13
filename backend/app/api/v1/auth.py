from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, create_access_token
from app.models.models import User, Settings
from app.schemas.schemas import UserResponse, SettingsResponse, SettingsUpdate
from typing import Dict

router = APIRouter()

@router.post("/login/google", response_model=Dict[str, str])
def login_google(body: Dict[str, str], db: Session = Depends(get_db)):
    user = get_current_user(db=db, token=None)
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/settings", response_model=SettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(Settings).filter(Settings.userId == current_user.id).first()
    if not settings:
        settings = Settings(userId=current_user.id, syncEmail=current_user.email)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/settings", response_model=SettingsResponse)
def update_settings(
    body: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(Settings).filter(Settings.userId == current_user.id).first()
    if not settings:
        settings = Settings(userId=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
    for var, value in body.model_dump(exclude_unset=True).items():
        setattr(settings, var, value)
        
    db.commit()
    db.refresh(settings)
    return settings
