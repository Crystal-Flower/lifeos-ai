from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.core.config import settings
from app.models.models import CalendarEvent
from sqlalchemy.orm import Session
from datetime import datetime
import json

class GoogleCalendarManager:
    def __init__(self, token_json_str: str = None):
        self.creds = None
        if token_json_str:
            try:
                creds_data = json.loads(token_json_str)
                self.creds = Credentials.from_authorized_user_info(creds_data)
            except Exception as e:
                print(f"Error loading google credentials: {e}")
                
    def is_authenticated(self) -> bool:
        return self.creds is not None and self.creds.valid
        
    def sync_events(self, db: Session, user_id: str, email: str = "anandhappriya@gmail.com"):
        if not self.is_authenticated():
            print("Google Calendar sync disabled: User not authenticated.")
            return False
            
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(
                calendarId=email,
                timeMin=now,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            gcal_events = events_result.get('items', [])
            
            for event in gcal_events:
                gevent_id = event['id']
                summary = event.get('summary', 'No Title')
                desc = event.get('description', '')
                start = event['start'].get('dateTime') or event['start'].get('date')
                end = event['end'].get('dateTime') or event['end'].get('date')
                
                # Normalize timezone string
                start = start.replace('Z', '+00:00')
                end = end.replace('Z', '+00:00')
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                
                db_event = db.query(CalendarEvent).filter(
                    CalendarEvent.googleEventId == gevent_id,
                    CalendarEvent.userId == user_id
                ).first()
                
                if db_event:
                    db_event.title = summary
                    db_event.description = desc
                    db_event.startTime = start_dt
                    db_event.endTime = end_dt
                else:
                    new_event = CalendarEvent(
                        userId=user_id,
                        googleEventId=gevent_id,
                        title=summary,
                        description=desc,
                        startTime=start_dt,
                        endTime=end_dt,
                        calendarEmail=email
                    )
                    db.add(new_event)
            db.commit()
            return True
        except Exception as e:
            print(f"Error syncing with Google Calendar: {e}")
            return False
            
    def create_event(self, event_data, email: str = "anandhappriya@gmail.com"):
        if not self.is_authenticated():
            return None
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            event_body = {
                'summary': event_data.title,
                'description': event_data.description,
                'start': {
                    'dateTime': event_data.startTime.isoformat() + 'Z',
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event_data.endTime.isoformat() + 'Z',
                    'timeZone': 'UTC',
                }
            }
            g_event = service.events().insert(calendarId=email, body=event_body).execute()
            return g_event.get('id')
        except Exception as e:
            print(f"Error creating calendar event on GCal: {e}")
            return None
