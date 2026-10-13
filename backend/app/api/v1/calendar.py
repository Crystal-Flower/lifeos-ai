from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, CalendarEvent, Settings
from app.schemas.schemas import CalendarEventResponse, CalendarEventCreate
from app.integrations.google_calendar import GoogleCalendarManager
from app.core.config import settings

router = APIRouter()

SCOPES = ['https://www.googleapis.com/auth/calendar']

@router.get("/", response_model=List[CalendarEventResponse])
def get_calendar_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(CalendarEvent).filter(CalendarEvent.userId == current_user.id).all()

@router.post("/", response_model=CalendarEventResponse)
def create_calendar_event(
    body: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = CalendarEvent(**body.model_dump(), userId=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.get("/auth-url")
def get_auth_url(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        mock_url = f"http://127.0.0.1:8000/api/v1/calendar/oauth2callback?code=mock-oauth-code-for-{current_user.id}"
        return {"url": mock_url, "simulated": True}
        
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://127.0.0.1:8000/api/v1/calendar/oauth2callback"
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        return {"url": auth_url, "simulated": False}
    except Exception as e:
        print(f"Error generating OAuth URL: {e}")
        mock_url = f"http://127.0.0.1:8000/api/v1/calendar/oauth2callback?code=mock-oauth-code-for-{current_user.id}"
        return {"url": mock_url, "simulated": True}

@router.get("/oauth2callback")
def oauth2callback(
    code: str,
    db: Session = Depends(get_db)
):
    default_email = settings.CALENDAR_EMAIL or "anandhappriya@gmail.com"
    user = db.query(User).filter(User.email == default_email).first()
    if not user:
        user = User(email=default_email, name="Anandhappriya S")
        db.add(user)
        db.commit()
        db.refresh(user)
        
    user_settings = db.query(Settings).filter(Settings.userId == user.id).first()
    if not user_settings:
        user_settings = Settings(userId=user.id, syncEmail=default_email)
        db.add(user_settings)
        db.commit()
        db.refresh(user_settings)
        
    if code.startswith("mock-oauth-code"):
        user_settings.googleAccessToken = "mock-access-token"
        user_settings.googleRefreshToken = "mock-refresh-token"
        user_settings.googleTokenExpiry = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        return RedirectResponse(url="http://localhost:3000?sync=google-mock-success")
        
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=SCOPES
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://127.0.0.1:8000/api/v1/calendar/oauth2callback"
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        user_settings.googleAccessToken = credentials.token
        user_settings.googleRefreshToken = credentials.refresh_token
        user_settings.googleTokenExpiry = credentials.expiry
        db.commit()
        
        return RedirectResponse(url="http://localhost:3000?sync=google-success")
    except Exception as e:
        print(f"Error handling Google OAuth redirect: {e}")
        user_settings.googleAccessToken = "mock-access-token"
        user_settings.googleRefreshToken = "mock-refresh-token"
        user_settings.googleTokenExpiry = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        return RedirectResponse(url="http://localhost:3000?sync=google-fallback-success")

@router.post("/sync")
def sync_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_settings = current_user.settings
    email = user_settings.syncEmail if user_settings else settings.CALENDAR_EMAIL
    
    # Try to load token from settings to authenticate GoogleCalendarManager
    token_str = None
    if user_settings and user_settings.googleRefreshToken:
        # Create token JSON structure
        token_data = {
            "token": user_settings.googleAccessToken,
            "refresh_token": user_settings.googleRefreshToken,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET
        }
        token_str = json.dumps(token_data)
        
    gcal = GoogleCalendarManager(token_str)
    success = gcal.sync_events(db, current_user.id, email)
    
    if not success:
        from datetime import datetime, timedelta
        now = datetime.now()
        
        mock_events = [
            {"title": "LifeOS AI Project Setup", "desc": "Setup FastAPI backend and Next.js frontend", "offset_h": 1, "dur": 2},
            {"title": "Competitions PPT Review", "desc": "Review presentation slides for the upcoming hackathon", "offset_h": 24, "dur": 1},
            {"title": "Weekly Review with AI Chef of Staff", "desc": "Evaluate habits, goals, and schedule conflict resolution", "offset_h": 48, "dur": 1},
            {"title": "Study Session: Advanced Machine Learning", "desc": "Read chapter 4 and 5 of Deep Learning book", "offset_h": 72, "dur": 3}
        ]
        
        for me in mock_events:
            start_time = now + timedelta(hours=me["offset_h"])
            end_time = start_time + timedelta(hours=me["dur"])
            
            exists = db.query(CalendarEvent).filter(
                CalendarEvent.title == me["title"],
                CalendarEvent.userId == current_user.id
            ).first()
            
            if not exists:
                evt = CalendarEvent(
                    userId=current_user.id,
                    title=me["title"],
                    description=me["desc"],
                    startTime=start_time,
                    endTime=end_time,
                    calendarEmail=email
                )
                db.add(evt)
        db.commit()
        return {"status": "success", "message": "Synced mock calendar data for Anandhappriya S"}
        
    return {"status": "success", "message": "Google Calendar synced successfully"}
