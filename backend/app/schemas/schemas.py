from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime

# Common types
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class SettingsBase(BaseModel):
    theme: str = "dark"
    googleSyncEnabled: bool = True
    telegramChatId: Optional[str] = None
    syncEmail: str = "anandhappriya@gmail.com"
    notificationTypes: List[str] = ["BROWSER", "EMAIL"]
    
    # OAuth Fields
    googleRefreshToken: Optional[str] = None
    googleAccessToken: Optional[str] = None
    googleTokenExpiry: Optional[datetime] = None

class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    googleSyncEnabled: Optional[bool] = None
    telegramChatId: Optional[str] = None
    syncEmail: Optional[str] = None
    notificationTypes: Optional[List[str]] = None
    googleRefreshToken: Optional[str] = None
    googleAccessToken: Optional[str] = None
    googleTokenExpiry: Optional[datetime] = None

class SettingsResponse(SettingsBase):
    id: str
    userId: str
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "TODO"
    priority: str = "MEDIUM"
    dueDate: Optional[datetime] = None
    estimatedMinutes: Optional[int] = None
    scheduledStart: Optional[datetime] = None
    scheduledEnd: Optional[datetime] = None
    projectId: Optional[str] = None
    competitionId: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    dueDate: Optional[datetime] = None
    estimatedMinutes: Optional[int] = None
    scheduledStart: Optional[datetime] = None
    scheduledEnd: Optional[datetime] = None
    projectId: Optional[str] = None
    competitionId: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "ACTIVE"
    dueDate: Optional[datetime] = None
    progress: float = 0.0
    
    # Extended fields
    githubRepo: Optional[str] = None
    dependencies: Optional[Dict[str, List[str]]] = None
    predictionData: Optional[Dict[str, Any]] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    dueDate: Optional[datetime] = None
    progress: Optional[float] = None
    githubRepo: Optional[str] = None
    dependencies: Optional[Dict[str, List[str]]] = None
    predictionData: Optional[Dict[str, Any]] = None

class ProjectResponse(ProjectBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class MilestoneBase(BaseModel):
    title: str
    dueDate: Optional[datetime] = None
    isCompleted: bool = False
    dependencies: Optional[List[str]] = None

class MilestoneCreate(MilestoneBase):
    projectId: str

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    dueDate: Optional[datetime] = None
    isCompleted: Optional[bool] = None
    dependencies: Optional[List[str]] = None

class MilestoneResponse(MilestoneBase):
    id: str
    projectId: str
    class Config:
        from_attributes = True

class TeamMemberBase(BaseModel):
    name: str
    role: Optional[str] = None
    email: Optional[str] = None

class TeamMemberCreate(TeamMemberBase):
    competitionId: str

class TeamMemberResponse(TeamMemberBase):
    id: str
    competitionId: str
    class Config:
        from_attributes = True

class CompetitionBase(BaseModel):
    title: str
    description: Optional[str] = None
    registrationUrl: Optional[str] = None
    deadline: Optional[datetime] = None
    reportSubmitted: bool = False
    pptSubmitted: bool = False
    demoLink: Optional[str] = None
    githubUrl: Optional[str] = None
    progress: float = 0.0
    
    # Extended fields
    timelineData: Optional[List[Dict[str, Any]]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    checklist: Optional[List[Dict[str, Any]]] = None

class CompetitionCreate(CompetitionBase):
    pass

class CompetitionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    registrationUrl: Optional[str] = None
    deadline: Optional[datetime] = None
    reportSubmitted: Optional[bool] = None
    pptSubmitted: Optional[bool] = None
    demoLink: Optional[str] = None
    githubUrl: Optional[str] = None
    progress: Optional[float] = None
    timelineData: Optional[List[Dict[str, Any]]] = None
    documents: Optional[List[Dict[str, Any]]] = None
    checklist: Optional[List[Dict[str, Any]]] = None

class CompetitionResponse(CompetitionBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    tags: List[str] = []

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None

class NoteResponse(NoteBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class HabitBase(BaseModel):
    name: str
    frequency: str = "DAILY"
    streak: int = 0

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    frequency: Optional[str] = None
    streak: Optional[int] = None

class HabitResponse(HabitBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class HabitLogBase(BaseModel):
    habitId: str
    date: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = True

class HabitLogResponse(HabitLogBase):
    id: str
    class Config:
        from_attributes = True

class GoalBase(BaseModel):
    title: str
    targetDate: Optional[datetime] = None
    progress: float = 0.0

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    targetDate: Optional[datetime] = None
    progress: Optional[float] = None

class GoalResponse(GoalBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class CalendarEventBase(BaseModel):
    googleEventId: Optional[str] = None
    title: str
    description: Optional[str] = None
    startTime: datetime
    endTime: datetime
    isAllDay: bool = False
    calendarEmail: str = "anandhappriya@gmail.com"

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventResponse(CalendarEventBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    class Config:
        from_attributes = True

class ReminderBase(BaseModel):
    taskId: Optional[str] = None
    scheduledTime: datetime
    channel: str = "BROWSER"
    urgencyLevel: str = "LOW"
    status: str = "PENDING"
    
    # Extended fields
    recurrence: str = "NONE"
    snoozeCount: int = 0
    escalationCount: int = 0
    contextData: Optional[Dict[str, Any]] = None

class ReminderResponse(ReminderBase):
    id: str
    userId: str
    createdAt: datetime
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: str
    userId: str
    title: str
    message: str
    isRead: bool
    createdAt: datetime
    class Config:
        from_attributes = True
