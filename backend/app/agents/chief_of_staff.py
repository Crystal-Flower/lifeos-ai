from sqlalchemy.orm import Session
from app.models.models import Task, CalendarEvent, Habit, Goal, Note, Project, Competition
from app.core.config import settings
from datetime import datetime, timedelta
import openai
import json

def get_system_briefing(db: Session, user_id: str) -> str:
    today = datetime.now().date()
    
    tasks_all = db.query(Task).filter(Task.userId == user_id).all()
    tasks_today = [t for t in tasks_all if t.status != "DONE" and (not t.dueDate or t.dueDate.date() <= today)]
    tasks_done = [t for t in tasks_all if t.status == "DONE"]
    
    missed_deadlines = [
        t for t in tasks_all 
        if t.status != "DONE" and t.dueDate and t.dueDate.date() < today
    ]
    
    events_today = db.query(CalendarEvent).filter(
        CalendarEvent.userId == user_id,
        CalendarEvent.startTime >= datetime(today.year, today.month, today.day),
        CalendarEvent.startTime < datetime(today.year, today.month, today.day) + timedelta(days=1)
    ).all()
    
    habits = db.query(Habit).filter(Habit.userId == user_id).all()
    goals = db.query(Goal).filter(Goal.userId == user_id).all()
    projects = db.query(Project).filter(Project.userId == user_id).all()
    competitions = db.query(Competition).filter(Competition.userId == user_id).all()
    
    completion_rate = (len(tasks_done) / len(tasks_all) * 100.0) if tasks_all else 100.0
    habit_score = sum(h.streak for h in habits)
    
    total_meeting_minutes = sum((e.endTime - e.startTime).seconds // 60 for e in events_today)
    high_priority_today = sum(1 for t in tasks_today if t.priority in ["HIGH", "URGENT"])
    
    burnout_risk = "LOW"
    burnout_msg = "Your schedule looks balanced today."
    if total_meeting_minutes > 240 and high_priority_today >= 3:
        burnout_risk = "HIGH"
        burnout_msg = "⚠️ High Burnout Risk: Over 4 hours of meetings and multiple high-priority tasks. Consider shifting non-urgent tasks."
    elif total_meeting_minutes > 180 or high_priority_today >= 4:
        burnout_risk = "MEDIUM"
        burnout_msg = "⚠️ Moderate Load: Take regular focus breaks to manage cognitive fatigue."
        
    conflicts = []
    events_sorted = sorted(events_today, key=lambda e: e.startTime)
    for i in range(len(events_sorted) - 1):
        e1 = events_sorted[i]
        e2 = events_sorted[i+1]
        if e1.endTime > e2.startTime:
            conflicts.append(f"Conflict: '{e1.title}' overlaps with '{e2.title}' between {e1.endTime.strftime('%H:%M')} and {e2.startTime.strftime('%H:%M')}.")
            
    briefing = f"--- EXECUTIVE DAILY BRIEFING FOR ANANDHAPPRIYA S ---\n"
    briefing += f"Date: {today.strftime('%A, %b %d, %Y')}\n\n"
    
    briefing += f"📊 Productivity Insights:\n"
    briefing += f" - Task Completion Rate: {completion_rate:.1f}%\n"
    briefing += f" - Habit Streak Score: {habit_score} pts\n"
    briefing += f" - Workspace Load: {burnout_msg}\n\n"
    
    if missed_deadlines:
        briefing += f"🚨 Missed Deadlines ({len(missed_deadlines)}):\n"
        for t in missed_deadlines:
            due_str = t.dueDate.strftime('%Y-%m-%d') if t.dueDate else ""
            briefing += f" - [OVERDUE] {t.title} (Was due: {due_str})\n"
        briefing += "\n"
        
    briefing += f"📅 Today's Schedule & Meetings ({len(events_today)}):\n"
    if events_today:
        for e in events_sorted:
            briefing += f" - {e.startTime.strftime('%H:%M')} - {e.endTime.strftime('%H:%M')}: {e.title}\n"
    else:
        briefing += " - No meetings scheduled.\n"
        
    briefing += f"\n📋 High-Priority Tasks Today ({len([t for t in tasks_today if t.priority in ['HIGH', 'URGENT']])}):\n"
    high_tasks = [t for t in tasks_today if t.priority in ['HIGH', 'URGENT']]
    if high_tasks:
        for t in high_tasks:
            est = f" ({t.estimatedMinutes}m)" if t.estimatedMinutes else ""
            briefing += f" - [{t.priority}] {t.title}{est}\n"
    else:
        briefing += " - None. Focus on standard goals.\n"
        
    briefing += f"\n🚀 Active Projects ({len(projects)}):\n"
    for p in projects:
        briefing += f" - {p.name} ({p.progress:.1f}% complete)\n"
        
    briefing += f"\n🏆 Competition Checklist Status ({len(competitions)}):\n"
    for c in competitions:
        briefing += f" - {c.title} (Progress: {c.progress:.1f}%, PPT: {'Done' if c.pptSubmitted else 'Pending'}, Report: {'Done' if c.reportSubmitted else 'Pending'})\n"
        
    if conflicts:
        briefing += "\n⚠️ Warnings & Overlaps:\n"
        for c in conflicts:
            briefing += f" - {c}\n"
            
    return briefing

async def get_ai_response(db: Session, user_id: str, user_message: str) -> str:
    msg_lower = user_message.lower()
    
    if "auto-schedule" in msg_lower or "schedule my day" in msg_lower or "run scheduler" in msg_lower:
        from app.services.ai_scheduler import run_ai_scheduler
        res = run_ai_scheduler(db, user_id)
        count = res.get("scheduledCount", 0)
        return f"Done! I ran the AI Scheduler. Scheduled {count} tasks. The schedule has been updated in real-time."
        
    if "next action" in msg_lower or "what should i do" in msg_lower:
        now = datetime.now()
        next_task = db.query(Task).filter(
            Task.userId == user_id,
            Task.status != "DONE",
            Task.scheduledStart >= now
        ).order_by(Task.scheduledStart).first()
        
        if next_task:
            return f"Your next scheduled action today is: '{next_task.title}' starting at {next_task.scheduledStart.strftime('%H:%M')}. Focus is key!"
        
        next_pri = db.query(Task).filter(
            Task.userId == user_id,
            Task.status != "DONE"
        ).order_by(Task.priority == "URGENT", Task.priority == "HIGH").first()
        
        if next_pri:
            return f"No scheduled slots remaining today, but your top priority task is: '{next_pri.title}' (Priority: {next_pri.priority}). Consider scheduling it."
            
        return "You have no pending tasks! You are all caught up."
        
    if "summarize" in msg_lower:
        keywords = msg_lower.replace("summarize", "").replace("note", "").strip().split()
        if keywords:
            notes = db.query(Note).filter(Note.userId == user_id).all()
            for note in notes:
                if any(k in note.title.lower() for k in keywords):
                    summary = note.summary or (note.content[:100] + "...")
                    return f"Here is the AI Summary for note '{note.title}':\n\n\"{summary}\""
                    
    briefing_context = get_system_briefing(db, user_id)
    if not settings.OPENAI_API_KEY:
        if "brief" in msg_lower or "today" in msg_lower:
            return briefing_context + "\n\nAI Recommendations:\n1. Solve overlaps first by adjusting the timings.\n2. Dedicate focus blocks for high-priority tasks."
        return f"Hello Anandhappriya! I am your LifeOS AI Chief of Staff. Currently, I am running in local-offline mode. Here is a summary of your workspace:\n\n{briefing_context}"
        
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        system_prompt = f"""
        You are the LifeOS AI Chief of Staff, a premium executive assistant for Anandhappriya S.
        You have direct visibility into the user's current day state:
        
        {briefing_context}
        
        Respond to the user's message in a helpful, highly polished, and professional tone.
        Suggest scheduling corrections, prioritize tasks, and offer productivity advice.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI engine: {e}\n\nHere is your workspace briefing:\n{briefing_context}"
