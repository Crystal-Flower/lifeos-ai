import asyncio
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Reminder, Task
from app.core.websocket_manager import ws_manager
from app.services.email_service import send_notification_email
from app.core.config import settings

async def start_reminder_worker():
    print("Starting background Reminder Worker loop...")
    while True:
        try:
            db = SessionLocal()
            now = datetime.utcnow()
            
            due_reminders = db.query(Reminder).filter(
                Reminder.scheduledTime <= now,
                Reminder.status == "PENDING"
            ).all()
            
            for reminder in due_reminders:
                reminder.status = "SENT"
                
                task_title = "General Alert"
                task_desc = ""
                task_done = False
                if reminder.taskId:
                    task = db.query(Task).filter(Task.id == reminder.taskId).first()
                    if task:
                        task_title = task.title
                        task_desc = task.description or ""
                        task_done = (task.status == "DONE")
                
                if task_done:
                    reminder.status = "CANCELLED"
                    continue
                    
                context_str = ""
                if reminder.contextData:
                    try:
                        ctx = reminder.contextData
                        if isinstance(ctx, str):
                            ctx = json.loads(ctx)
                        if "location" in ctx:
                            context_str = f" [Context: at {ctx['location']}]"
                    except Exception:
                        pass
                
                payload = {
                    "type": "REMINDER",
                    "id": reminder.id,
                    "title": f"Reminder Alert! [Priority: {reminder.urgencyLevel}]{context_str}",
                    "message": f"Task: {task_title}",
                    "urgency": reminder.urgencyLevel
                }
                
                await ws_manager.send_personal_message(payload, reminder.userId)
                print(f"Sent real-time reminder notification for task: {task_title}")
                
                target_email = settings.CALENDAR_EMAIL or "anandhappriya@gmail.com"
                send_notification_email(
                    subject=f"LifeOS AI Reminder: {task_title}",
                    body=f"Hello Anandhappriya,\n\nThis is a reminder from your LifeOS AI Chief of Staff.\n\nTask: {task_title}\nDescription: {task_desc}\nUrgency: {reminder.urgencyLevel}{context_str}\n\nKeep up the great work!\n- LifeOS AI",
                    to_email=target_email
                )
                
                if reminder.recurrence in ["DAILY", "WEEKLY"]:
                    days_to_add = 1 if reminder.recurrence == "DAILY" else 7
                    next_time = reminder.scheduledTime + timedelta(days=days_to_add)
                    
                    new_reminder = Reminder(
                        userId=reminder.userId,
                        taskId=reminder.taskId,
                        scheduledTime=next_time,
                        channel=reminder.channel,
                        urgencyLevel=reminder.urgencyLevel,
                        status="PENDING",
                        recurrence=reminder.recurrence,
                        contextData=reminder.contextData
                    )
                    db.add(new_reminder)
                    print(f"Scheduled recurring reminder ({reminder.recurrence}) for {next_time}")
            
            # Process Escalations (e.g. check for SENT reminders > 2 minutes ago)
            escalate_limit = now - timedelta(minutes=2)
            active_sent_reminders = db.query(Reminder).filter(
                Reminder.status == "SENT",
                Reminder.urgencyLevel == "ESCALATING",
                Reminder.scheduledTime <= escalate_limit
            ).all()
            
            for reminder in active_sent_reminders:
                if reminder.taskId:
                    task = db.query(Task).filter(Task.id == reminder.taskId).first()
                    if task and task.status != "DONE":
                        reminder.escalationCount += 1
                        reminder.scheduledTime = now
                        
                        payload = {
                            "type": "REMINDER",
                            "id": reminder.id,
                            "title": f"⚠️ ESCALATED WARNING ({reminder.escalationCount})",
                            "message": f"CRITICAL: Task is still incomplete: {task.title}",
                            "urgency": "URGENT"
                        }
                        
                        await ws_manager.send_personal_message(payload, reminder.userId)
                        
                        target_email = settings.CALENDAR_EMAIL or "anandhappriya@gmail.com"
                        send_notification_email(
                            subject=f"⚠️ ESCALATED LifeOS AI Warning: {task.title}",
                            body=f"Hello Anandhappriya,\n\nThis is an escalated warning from your LifeOS AI Chief of Staff.\n\nYour task: '{task.title}' remains incomplete after several prompts. Please address this immediately.\n\nEscalation Level: {reminder.escalationCount}\n\n- LifeOS AI",
                            to_email=target_email
                        )
                        print(f"Escalated reminder for task: {task.title}")
            
            db.commit()
            db.close()
        except Exception as e:
            print(f"Error in reminder worker loop: {e}")
            
        await asyncio.sleep(5)
