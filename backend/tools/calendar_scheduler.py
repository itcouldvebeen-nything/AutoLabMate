"""
Calendar Scheduler - Google Calendar integration
Schedules equipment bookings and experiment time slots
"""

import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CalendarScheduler:
    """
    Calendar Scheduler for equipment booking
    
    Integrates with Google Calendar API to schedule experiments
    """
    
    def __init__(self):
        """Initialize Calendar Scheduler"""
        self.use_mock = os.getenv("MOCK_MODE", "true").lower() == "true"
        self.service = None
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        
        if not self.use_mock:
            self._initialize_google_calendar()
        else:
            self._initialize_mock()
    
    def _initialize_google_calendar(self):
        """Initialize Google Calendar client"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            import json
            
            credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH")
            if not credentials_path:
                raise ValueError("GOOGLE_CALENDAR_CREDENTIALS_PATH not set")
            
            # Load credentials
            with open(credentials_path) as f:
                creds_json = json.load(f)
            
            credentials = service_account.Credentials.from_service_account_info(creds_json)
            
            # Build service
            self.service = build("calendar", "v3", credentials=credentials)
            logger.info("Google Calendar initialized successfully")
            
        except Exception as e:
            logger.warning(f"Google Calendar initialization failed: {str(e)}, using mock")
            self.use_mock = True
            self._initialize_mock()
    
    def _initialize_mock(self):
        """Initialize mock calendar"""
        self.mock_events = []
        logger.info("Calendar scheduler running in MOCK mode")
    
    async def schedule_experiment(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule an experiment in calendar
        
        Args:
            experiment_data: Experiment details
                - title: Event title
                - start_time: Start datetime
                - duration: Duration in minutes
                - equipment: Equipment name
                - location: Location
        
        Returns:
            Event ID and calendar URL
        """
        try:
            if self.use_mock:
                return await self._schedule_mock(experiment_data)
            else:
                return await self._schedule_google(experiment_data)
                
        except Exception as e:
            logger.error(f"Scheduling error: {str(e)}")
            raise
    
    async def _schedule_mock(self, experiment_data: Dict) -> Dict[str, Any]:
        """Mock scheduling implementation"""
        import uuid
        
        event_id = f"mock_event_{uuid.uuid4().hex[:8]}"
        
        title = experiment_data.get("title", "Lab Experiment")
        start_time = experiment_data.get("start_time", datetime.now())
        duration = experiment_data.get("duration", 60)
        
        self.mock_events.append({
            "id": event_id,
            "title": title,
            "start_time": start_time,
            "duration": duration
        })
        
        logger.info(f"Mock event scheduled: {event_id}")
        
        return {
            "event_id": event_id,
            "calendar_url": f"https://calendar.google.com/mock/{event_id}",
            "status": "scheduled"
        }
    
    async def _schedule_google(self, experiment_data: Dict) -> Dict[str, Any]:
        """Google Calendar implementation"""
        title = experiment_data.get("title", "Lab Experiment")
        start_time = experiment_data.get("start_time", datetime.now())
        duration = experiment_data.get("duration", 60)
        equipment = experiment_data.get("equipment", "")
        location = experiment_data.get("location", "")
        
        # Create event
        event = {
            "summary": title,
            "location": location,
            "description": f"Equipment: {equipment}\nScheduled by AutoLabMate",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": (start_time + timedelta(minutes=duration)).isoformat(),
                "timeZone": "UTC"
            }
        }
        
        # Insert event
        created_event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event
        ).execute()
        
        logger.info(f"Google Calendar event scheduled: {created_event['id']}")
        
        return {
            "event_id": created_event["id"],
            "calendar_url": created_event["htmlLink"],
            "status": "scheduled"
        }
    
    def is_available(self) -> bool:
        """Check if calendar service is available"""
        return True  # Always available (mock or real)

