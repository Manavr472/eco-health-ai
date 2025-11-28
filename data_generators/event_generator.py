"""
Event Calendar Generator for Mumbai
Generates calendar of major festivals and events that impact healthcare
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_START_DATE, DATA_END_DATE, ANNUAL_FESTIVALS


class EventGenerator:
    """Generate event calendar for Mumbai"""
    
    def __init__(self):
        self.start_date = DATA_START_DATE
        self.end_date = DATA_END_DATE
        self.festivals = ANNUAL_FESTIVALS
    
    def generate(self):
        """Generate complete event calendar"""
        events = []
        
        print(f"Generating event calendar from {self.start_date} to {self.end_date}...")
        
        for festival_name, occurrences in self.festivals.items():
            for occurrence in occurrences:
                start_date = datetime.strptime(occurrence["start"], "%Y-%m-%d")
                end_date = datetime.strptime(occurrence["end"], "%Y-%m-%d")
                
                # Only include if within our data range
                if start_date <= self.end_date and end_date >= self.start_date:
                    # Calculate duration
                    duration = (end_date - start_date).days + 1
                    
                    # Determine impact type
                    impact_type = self._get_impact_type(festival_name)
                    impact_severity = self._get_impact_severity(festival_name)
                    
                    events.append({
                        'festival_name': festival_name,
                        'start_date': start_date,
                        'end_date': end_date,
                        'duration_days': duration,
                        'impact_type': impact_type,
                        'impact_severity': impact_severity,
                        'year': start_date.year
                    })
        
        df = pd.DataFrame(events)
        df = df.sort_values('start_date').reset_index(drop=True)
        
        print(f"Generated {len(df)} festival events")
        print(f"\nEvents by festival:")
        print(df.groupby('festival_name').size())
        
        return df
    
    def _get_impact_type(self, festival_name):
        """Determine the type of healthcare impact"""
        impact_map = {
            "Diwali": "Respiratory & Burns",
            "Ganesh Chaturthi": "Trauma & Accidents",
            "Holi": "Eye/Skin Injuries",
            "Navratri": "Fatigue & Accidents"
        }
        return impact_map.get(festival_name, "General")
    
    def _get_impact_severity(self, festival_name):
        """Rate the severity of healthcare impact (1-5)"""
        severity_map = {
            "Diwali": 5,  # Highest - major pollution spike
            "Ganesh Chaturthi": 4,  # High - large crowds, accidents
            "Holi": 3,  # Moderate - injuries
            "Navratri": 2  # Low-Moderate - fatigue
        }
        return severity_map.get(festival_name, 1)
    
    def create_daily_event_marker(self, events_df):
        """Create daily dataset marking which days have events"""
        # Create date range
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        daily_data = []
        
        for date in date_range:
            # Check if any event is active on this date
            active_events = []
            total_severity = 0
            
            for _, event in events_df.iterrows():
                if event['start_date'] <= date <= event['end_date']:
                    active_events.append(event['festival_name'])
                    total_severity += event['impact_severity']
            
            # Also mark pre-event and post-event periods
            pre_event = []
            post_event = []
            
            for _, event in events_df.iterrows():
                # 3 days before event (preparation period)
                if (event['start_date'] - timedelta(days=3)) <= date < event['start_date']:
                    pre_event.append(event['festival_name'])
                
                # 3 days after event (recovery period)
                if event['end_date'] < date <= (event['end_date'] + timedelta(days=3)):
                    post_event.append(event['festival_name'])
            
            daily_data.append({
                'date': date,
                'has_event': len(active_events) > 0,
                'active_events': ', '.join(active_events) if active_events else None,
                'event_severity': total_severity,
                'is_pre_event': len(pre_event) > 0,
                'is_post_event': len(post_event) > 0,
                'pre_event_names': ', '.join(pre_event) if pre_event else None,
                'post_event_names': ', '.join(post_event) if post_event else None
            })
        
        daily_df = pd.DataFrame(daily_data)
        print(f"\nDaily event markers created: {len(daily_df)} days")
        print(f"Days with active events: {daily_df['has_event'].sum()}")
        
        return daily_df
    
    def save(self, events_df, daily_df, 
             events_path="data/events.csv",
             daily_path="data/daily_events.csv"):
        """Save event data to CSV"""
        os.makedirs(os.path.dirname(events_path), exist_ok=True)
        
        events_df.to_csv(events_path, index=False)
        daily_df.to_csv(daily_path, index=False)
        
        print(f"Saved events to {events_path}")
        print(f"Saved daily event markers to {daily_path}")


if __name__ == "__main__":
    generator = EventGenerator()
    events_df = generator.generate()
    daily_df = generator.create_daily_event_marker(events_df)
    generator.save(events_df, daily_df)
    
    # Display sample
    print("\nUpcoming events (sample):")
    print(events_df.head(10))
    print("\nSample daily event markers:")
    print(daily_df[daily_df['has_event']].head(10))
