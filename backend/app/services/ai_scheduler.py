from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.models import Task, CalendarEvent
import json

def get_free_time_slots(events: list, day_start: datetime, day_end: datetime) -> list:
    sorted_events = sorted(events, key=lambda e: e.startTime)
    
    free_slots = []
    current_time = day_start
    
    for event in sorted_events:
        if event.startTime > current_time:
            if event.startTime > day_start and current_time < day_end:
                slot_start = max(current_time, day_start)
                slot_end = min(event.startTime, day_end)
                if slot_end > slot_start:
                    free_slots.append((slot_start, slot_end))
        current_time = max(current_time, event.endTime)
        
    if current_time < day_end:
        free_slots.append((current_time, day_end))
        
    return free_slots

def run_ai_scheduler(db: Session, user_id: str) -> dict:
    now = datetime.now()
    
    tasks = db.query(Task).filter(
        Task.userId == user_id,
        Task.status != "DONE"
    ).all()
    
    priority_weight = {"URGENT": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    tasks_sorted = sorted(
        tasks,
        key=lambda t: (-priority_weight.get(t.priority, 2), t.dueDate or datetime.max)
    )
    
    start_period = now.replace(hour=0, minute=0, second=0)
    end_period = start_period + timedelta(days=7)
    events = db.query(CalendarEvent).filter(
        CalendarEvent.userId == user_id,
        CalendarEvent.startTime >= start_period,
        CalendarEvent.startTime < end_period
    ).all()
    
    scheduled_count = 0
    warnings = []
    
    day_cursor = start_period
    task_index = 0
    
    while day_cursor < end_period and task_index < len(tasks_sorted):
        day_start = day_cursor.replace(hour=8, minute=0, second=0)
        day_end = day_cursor.replace(hour=22, minute=0, second=0)
        
        day_events = [
            e for e in events 
            if e.startTime >= day_start.replace(hour=0, minute=0, second=0) 
            and e.startTime < day_start.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        ]
        
        free_slots = get_free_time_slots(day_events, day_start, day_end)
        
        for slot_start, slot_end in free_slots:
            slot_duration = (slot_end - slot_start).seconds // 60
            
            while task_index < len(tasks_sorted) and slot_duration >= 15:
                task = tasks_sorted[task_index]
                task_duration = task.estimatedMinutes or 45
                
                if slot_duration >= task_duration:
                    task.scheduledStart = slot_start
                    task.scheduledEnd = slot_start + timedelta(minutes=task_duration)
                    
                    slot_start = task.scheduledEnd
                    slot_duration -= task_duration
                    task_index += 1
                    scheduled_count += 1
                else:
                    break
                    
        day_cursor += timedelta(days=1)
        
    db.commit()
    
    daily_plans = []
    for d in range(7):
        day_date = (start_period + timedelta(days=d)).date()
        day_start_dt = datetime.combine(day_date, datetime.min.time())
        day_end_dt = day_start_dt + timedelta(days=1)
        
        day_events = db.query(CalendarEvent).filter(
            CalendarEvent.userId == user_id,
            CalendarEvent.startTime >= day_start_dt,
            CalendarEvent.startTime < day_end_dt
        ).all()
        
        day_tasks = db.query(Task).filter(
            Task.userId == user_id,
            Task.scheduledStart >= day_start_dt,
            Task.scheduledStart < day_end_dt
        ).all()
        
        blocks = []
        for e in day_events:
            blocks.append({
                "id": e.id,
                "type": "EVENT",
                "title": e.title,
                "start": e.startTime.isoformat(),
                "end": e.endTime.isoformat()
            })
        for t in day_tasks:
            blocks.append({
                "id": t.id,
                "type": "TASK",
                "title": t.title,
                "priority": t.priority,
                "start": t.scheduledStart.isoformat(),
                "end": t.scheduledEnd.isoformat()
            })
            
        blocks_sorted = sorted(blocks, key=lambda b: b["start"])
        
        daily_plans.append({
            "date": day_date.isoformat(),
            "dayName": day_date.strftime("%A"),
            "blocks": blocks_sorted
        })
        
    if task_index < len(tasks_sorted):
        warnings.append(f"{len(tasks_sorted) - task_index} task(s) could not be scheduled in the next 7 days due to calendar capacity.")
        
    return {
        "status": "success",
        "scheduledCount": scheduled_count,
        "warnings": warnings,
        "dailyPlans": daily_plans
    }
