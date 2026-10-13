from fastapi import APIRouter
from app.api.v1 import auth, tasks, habits, projects, competitions, notes, calendar, ai, scheduler, reminders, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(competitions.router, prefix="/competitions", tags=["competitions"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
