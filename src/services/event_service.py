from datetime import datetime
import logging

class EventService:
    """Service to manage festival and seasonal events"""
    
    def __init__(self):
        self.logger = logging.getLogger('prediction_agent')
        
        # Static event calendar for Mumbai (2024-2025)
        self.events = {
            '2024-11-01': {'name': 'Diwali', 'type': 'pollution', 'duration': 5},
            '2025-10-20': {'name': 'Diwali', 'type': 'pollution', 'duration': 5},
            '2024-09-07': {'name': 'Ganesh Chaturthi', 'type': 'crowd', 'duration': 10},
            '2025-08-27': {'name': 'Ganesh Chaturthi', 'type': 'crowd', 'duration': 10},
        }
        
    def get_events(self, date_str: str):
        """Check for active events on a given date"""
        active_events = []
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Check specific festivals
        for start_date_str, details in self.events.items():
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            duration = details['duration']
            
            # If date falls within [start, start + duration]
            delta = (target_date - start_date).days
            if 0 <= delta < duration:
                active_events.append(details['name'])
                
        # Check Monsoon Season (June - September)
        if 6 <= target_date.month <= 9:
            active_events.append('Monsoon Season')
            
        return active_events

# Singleton instance
event_service = EventService()
