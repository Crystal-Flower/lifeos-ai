from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User, Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_current_user(db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)) -> User:
    # Single-user mode: retrieve or create the default user based on settings
    default_email = settings.CALENDAR_EMAIL or "anandhappriya@gmail.com"
    default_user = db.query(User).filter(User.email == default_email).first()
    
    if not default_user:
        default_user = User(email=default_email, name="Anandhappriya S")
        db.add(default_user)
        db.commit()
        db.refresh(default_user)
        
        # Initialize default settings
        user_settings = Settings(userId=default_user.id, theme="dark", syncEmail=default_email)
        db.add(user_settings)
        db.commit()
    
    if not token:
        return default_user
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            return default_user
    except jwt.JWTError:
        return default_user
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return default_user
    return user
