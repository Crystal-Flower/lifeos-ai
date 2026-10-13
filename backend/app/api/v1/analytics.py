from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Task, Habit, CalendarEvent

router = APIRouter()

@router.get("/")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.now().date()
    
    tasks_all = db.query(Task).filter(Task.userId == current_user.id).all()
    tasks_done = [t for t in tasks_all if t.status == "DONE"]
    tasks_todo = [t for t in tasks_all if t.status != "DONE"]
    
    completion_rate = (len(tasks_done) / len(tasks_all) * 100.0) if tasks_all else 100.0
    focus_time_done = sum(t.estimatedMinutes for t in tasks_done if t.estimatedMinutes) or 0
    
    missed_deadlines = sum(
        1 for t in tasks_todo 
        if t.dueDate and t.dueDate.date() < today
    )
    
    habits = db.query(Habit).filter(Habit.userId == current_user.id).all()
    habit_score = sum(h.streak for h in habits)
    
    events_today = db.query(CalendarEvent).filter(
        CalendarEvent.userId == current_user.id,
        CalendarEvent.startTime >= datetime(today.year, today.month, today.day),
        CalendarEvent.startTime < datetime(today.year, today.month, today.day) + timedelta(days=1)
    ).all()
    
    total_meeting_minutes = sum((e.endTime - e.startTime).seconds // 60 for e in events_today)
    high_priority_today = sum(1 for t in tasks_todo if t.dueDate and t.dueDate.date() <= today and t.priority in ["HIGH", "URGENT"])
    
    burnout_risk = "LOW"
    if total_meeting_minutes > 240 and high_priority_today >= 3:
        burnout_risk = "HIGH"
    elif total_meeting_minutes > 180 or high_priority_today >= 4:
        burnout_risk = "MEDIUM"
        
    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)
        
        # Count items completed on this calendar day
        day_done = sum(1 for t in tasks_done if t.updatedAt and day_start <= t.updatedAt < day_end)
        # Seed default total
        day_total = sum(1 for t in tasks_all if t.createdAt and t.createdAt < day_end)
        
        chart_data.append({
            "date": day.strftime("%b %d"),
            "completed": day_done,
            "total": day_total if day_total > 0 else 1
        })
        
    return {
        "completionRate": round(completion_rate, 1),
        "focusTimeMinutes": focus_time_done,
        "missedDeadlinesCount": missed_deadlines,
        "burnoutRisk": burnout_risk,
        "habitScore": habit_score,
        "chartData": chart_data
    }
