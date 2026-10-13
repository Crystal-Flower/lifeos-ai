from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    settings = relationship("Settings", uselist=False, back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    habits = relationship("Habit", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    competitions = relationship("Competition", back_populates="user", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    events = relationship("CalendarEvent", back_populates="user", cascade="all, delete-orphan")

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    theme = Column(String, default="dark")
    googleSyncEnabled = Column(Boolean, default=True)
    telegramChatId = Column(String, nullable=True)
    syncEmail = Column(String, default="anandhappriya@gmail.com")
    notificationTypes = Column(JSON, default=lambda: ["BROWSER", "EMAIL"])
    
    # Google OAuth fields
    googleRefreshToken = Column(String, nullable=True)
    googleAccessToken = Column(String, nullable=True)
    googleTokenExpiry = Column(DateTime, nullable=True)
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="settings")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="TODO") # TODO, IN_PROGRESS, DONE, ARCHIVED
    priority = Column(String, default="MEDIUM") # LOW, MEDIUM, HIGH, URGENT
    dueDate = Column(DateTime, nullable=True)
    estimatedMinutes = Column(Integer, nullable=True)
    scheduledStart = Column(DateTime, nullable=True)
    scheduledEnd = Column(DateTime, nullable=True)
    projectId = Column(String, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    competitionId = Column(String, ForeignKey("competitions.id", ondelete="SET NULL"), nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    competition = relationship("Competition", back_populates="tasks")
    reminders = relationship("Reminder", back_populates="task", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")
    dueDate = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    
    # Extended Project fields
    githubRepo = Column(String, nullable=True)
    dependencies = Column(JSON, nullable=True) # e.g. {"milestone_id": ["dep_milestone_id"]}
    predictionData = Column(JSON, nullable=True) # e.g. {"predictedCompletionDate": "ISOString", "burnUpRate": 0.5}

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")

class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    projectId = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    dueDate = Column(DateTime, nullable=True)
    isCompleted = Column(Boolean, default=False)
    dependencies = Column(JSON, nullable=True) # List of dependent milestone IDs
    
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="milestones")

class Competition(Base):
    __tablename__ = "competitions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    registrationUrl = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    reportSubmitted = Column(Boolean, default=False)
    pptSubmitted = Column(Boolean, default=False)
    demoLink = Column(String, nullable=True)
    githubUrl = Column(String, nullable=True)
    progress = Column(Float, default=0.0)
    
    # Extended Competition fields
    timelineData = Column(JSON, nullable=True) # Key checkpoints and deadlines
    documents = Column(JSON, nullable=True) # Linked documents e.g. [{"name": "Report Outline", "url": "..."}]
    checklist = Column(JSON, nullable=True) # Detailed checklist of submission criteria

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="competitions")
    tasks = relationship("Task", back_populates="competition")
    teamMembers = relationship("TeamMember", back_populates="competition", cascade="all, delete-orphan")

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    competitionId = Column(String, ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    competition = relationship("Competition", back_populates="teamMembers")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    tags = Column(JSON, default=list)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="notes")

class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    frequency = Column(String, default="DAILY") # DAILY, WEEKLY
    streak = Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="habits")
    history = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")

class HabitLog(Base):
    __tablename__ = "habit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    habitId = Column(String, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=True)
    
    habit = relationship("Habit", back_populates="history")

class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    targetDate = Column(DateTime, nullable=True)
    progress = Column(Float, default=0.0)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    googleEventId = Column(String, unique=True, nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime, nullable=False)
    isAllDay = Column(Boolean, default=False)
    calendarEmail = Column(String, default="anandhappriya@gmail.com")
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="events")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    taskId = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    scheduledTime = Column(DateTime, nullable=False)
    channel = Column(String, default="BROWSER") # BROWSER, EMAIL, TELEGRAM
    urgencyLevel = Column(String, default="LOW") # LOW, MEDIUM, ESCALATING
    status = Column(String, default="PENDING") # PENDING, SENT, SNOOZED, CANCELLED
    
    # Extended Reminder fields
    recurrence = Column(String, default="NONE") # NONE, DAILY, WEEKLY
    snoozeCount = Column(Integer, default=0)
    escalationCount = Column(Integer, default=0)
    contextData = Column(JSON, nullable=True) # e.g. {"location": "work", "lastEscalatedTime": "..."}

    createdAt = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reminders")
    task = relationship("Task", back_populates="reminders")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    userId = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    isRead = Column(Boolean, default=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")

class File(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    projectId = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="files")
