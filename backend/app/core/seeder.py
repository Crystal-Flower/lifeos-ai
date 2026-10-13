from sqlalchemy.orm import Session
from app.models.models import User, Settings, Task, Habit, Goal, Note, CalendarEvent, Project, Competition
from datetime import datetime, timedelta

def seed_database(db: Session):
    default_email = "anandhappriya@gmail.com"
    user = db.query(User).filter(User.email == default_email).first()
    if user:
        return
        
    print("Seeding database with default workspace data for Anandhappriya S...")
    
    user = User(email=default_email, name="Anandhappriya S")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    settings_obj = Settings(userId=user.id, theme="dark", syncEmail=default_email)
    db.add(settings_obj)
    db.commit()
    
    tasks = [
        Task(userId=user.id, title="Setup LifeOS AI Platform skeleton", status="IN_PROGRESS", priority="URGENT", estimatedMinutes=60),
        Task(userId=user.id, title="Draft Competitions Review PPT", status="TODO", priority="HIGH", estimatedMinutes=45),
        Task(userId=user.id, title="Verify Google Calendar sync tokens", status="DONE", priority="MEDIUM", estimatedMinutes=20)
    ]
    for t in tasks:
        db.add(t)
        
    projects = [
        Project(userId=user.id, name="LifeOS Core Engine", description="FastAPI and Next.js development workspace", progress=50.0, status="ACTIVE"),
        Project(userId=user.id, name="Second Brain Sync API", description="Supabase storage and note summarizer", progress=20.0, status="ON_HOLD")
    ]
    for p in projects:
        db.add(p)
        
    comps = [
        Competition(userId=user.id, title="Global AI Productivity Hackathon", description="Building the ultimate LifeOS agent suite", progress=50.0, reportSubmitted=True, pptSubmitted=True, githubUrl="https://github.com/anandhappriya")
    ]
    for c in comps:
        db.add(c)
        
    notes = [
        Note(userId=user.id, title="Agentic Architectures", content="Multi-agent frameworks benefit from specialized node routing like LangGraph. Shared memory states are vital.", summary="Multi-agent workflows run best with routing states and modular node designs.", tags=["AI", "Architectures"])
    ]
    for n in notes:
        db.add(n)
        
    habits = [
        Habit(userId=user.id, name="Code daily", streak=5, frequency="DAILY"),
        Habit(userId=user.id, name="Read research papers", streak=2, frequency="DAILY")
    ]
    for h in habits:
        db.add(h)
        
    goals = [
        Goal(userId=user.id, title="Launch LifeOS AI v1.0", progress=45.0)
    ]
    for g in goals:
        db.add(g)
        
    now = datetime.now()
    events = [
        CalendarEvent(userId=user.id, title="LifeOS AI Project Setup", description="Setup FastAPI backend and Next.js frontend", startTime=now + timedelta(hours=1), endTime=now + timedelta(hours=3), calendarEmail=default_email)
    ]
    for e in events:
        db.add(e)
        
    db.commit()
    print("Database seeding completed.")
