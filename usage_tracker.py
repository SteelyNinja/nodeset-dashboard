import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import streamlit as st
from collections import defaultdict

class UsageTracker:
    """Tracks usage statistics for the dashboard and stores them in a JSON file"""
    
    def __init__(self, stats_file='usage_stats.json'):
        self.stats_file = stats_file
        self.stats = self._load_stats()
        
    def _load_stats(self) -> Dict[str, Any]:
        """Load existing statistics from JSON file"""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        
        # Return simplified structure
        return {
            'total_visits': 0,
            'daily_visits': {},
            'session_data': {},
            'user_agents': {},
            'first_visit': None,
            'last_visit': None,
            'hourly_distribution': {str(i): 0 for i in range(24)},
            'daily_distribution': {str(i): 0 for i in range(7)},  # 0=Monday, 6=Sunday
            'monthly_visits': {}
        }
    
    def _save_stats(self):
        """Save current statistics to JSON file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except IOError as e:
            st.error(f"Failed to save usage statistics: {e}")
    
    def track_visit(self, user_agent: Optional[str] = None):
        """Track a user visit (session start only)"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        hour = str(now.hour)
        day_of_week = str(now.weekday())
        month = now.strftime('%Y-%m')
        
        # Get or create session
        session_id = self._get_session_id()
        is_new_session = session_id not in self.stats['session_data']
        
        # Only count as visit if it's a NEW session
        if is_new_session:
            # Update basic counters (only for new sessions)
            self.stats['total_visits'] += 1
            
            # Update daily visits
            if today not in self.stats['daily_visits']:
                self.stats['daily_visits'][today] = 0
            self.stats['daily_visits'][today] += 1
            
            # Update monthly visits
            if month not in self.stats['monthly_visits']:
                self.stats['monthly_visits'][month] = 0
            self.stats['monthly_visits'][month] += 1
            
            # Update hourly distribution
            self.stats['hourly_distribution'][hour] += 1
            
            # Update daily distribution (day of week)
            self.stats['daily_distribution'][day_of_week] += 1
            
            # Track user agent
            if user_agent:
                if user_agent not in self.stats['user_agents']:
                    self.stats['user_agents'][user_agent] = 0
                self.stats['user_agents'][user_agent] += 1
            
            # Update first/last visit timestamps
            if self.stats['first_visit'] is None:
                self.stats['first_visit'] = now.isoformat()
            self.stats['last_visit'] = now.isoformat()
            
            # Create simplified session data
            self.stats['session_data'][session_id] = {
                'first_visit': now.isoformat(),
                'last_activity': now.isoformat()
            }
        else:
            # Existing session - just update activity
            self.stats['session_data'][session_id]['last_activity'] = now.isoformat()
        
        self._save_stats()
    
    
    def _get_session_id(self) -> str:
        """Generate or retrieve session ID"""
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state['session_id'] = str(uuid.uuid4())
        return st.session_state['session_id']
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get a simplified summary of current statistics"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Calculate active sessions (last activity within 30 minutes)
        active_sessions = 0
        for session_data in self.stats['session_data'].values():
            last_activity = datetime.fromisoformat(session_data['last_activity'])
            if (now - last_activity).total_seconds() < 1800:  # 30 minutes
                active_sessions += 1
        
        return {
            'total_visits': self.stats['total_visits'],
            'visits_today': self.stats['daily_visits'].get(today, 0),
            'visits_yesterday': self.stats['daily_visits'].get(yesterday, 0),
            'total_sessions': len(self.stats['session_data']),
            'active_sessions': active_sessions,
            'peak_hour': max(self.stats['hourly_distribution'].items(), key=lambda x: x[1])[0] if any(self.stats['hourly_distribution'].values()) else 'none',
            'first_visit': self.stats['first_visit'],
            'last_visit': self.stats['last_visit']
        }
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Get simplified detailed statistics for the admin page"""
        return {
            'summary': self.get_stats_summary(),
            'daily_visits': self.stats['daily_visits'],
            'hourly_distribution': self.stats['hourly_distribution'],
            'daily_distribution': self.stats['daily_distribution'],
            'monthly_visits': self.stats['monthly_visits'],
            'user_agents': self.stats['user_agents'],
            'session_count': len(self.stats['session_data'])
        }
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """Remove session data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        sessions_to_remove = []
        for session_id, session_data in self.stats['session_data'].items():
            last_activity = datetime.fromisoformat(session_data['last_activity'])
            if last_activity < cutoff_date:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.stats['session_data'][session_id]
        
        if sessions_to_remove:
            self._save_stats()
        
        return len(sessions_to_remove)
    
    def reset_visit_counts(self):
        """Reset visit counts to match actual sessions (for fixing inflated counts)"""
        # Reset visit counters to match actual unique sessions
        total_sessions = len(self.stats['session_data'])
        
        # Reset total visits to session count
        self.stats['total_visits'] = total_sessions
        
        # Recalculate daily visits based on sessions
        daily_sessions = {}
        monthly_sessions = {}
        hourly_sessions = {}
        daily_dist_sessions = {}
        
        for session_data in self.stats['session_data'].values():
            first_visit = datetime.fromisoformat(session_data['first_visit'])
            date_str = first_visit.strftime('%Y-%m-%d')
            month_str = first_visit.strftime('%Y-%m')
            hour_str = str(first_visit.hour)
            day_of_week_str = str(first_visit.weekday())
            
            daily_sessions[date_str] = daily_sessions.get(date_str, 0) + 1
            monthly_sessions[month_str] = monthly_sessions.get(month_str, 0) + 1
            hourly_sessions[hour_str] = hourly_sessions.get(hour_str, 0) + 1
            daily_dist_sessions[day_of_week_str] = daily_dist_sessions.get(day_of_week_str, 0) + 1
        
        # Update stats with corrected values
        self.stats['daily_visits'] = daily_sessions
        self.stats['monthly_visits'] = monthly_sessions
        
        # Reset hourly distribution
        for hour in range(24):
            hour_str = str(hour)
            self.stats['hourly_distribution'][hour_str] = hourly_sessions.get(hour_str, 0)
        
        # Reset daily distribution
        for day in range(7):
            day_str = str(day)
            self.stats['daily_distribution'][day_str] = daily_dist_sessions.get(day_str, 0)
        
        self._save_stats()
        return total_sessions
    
    def reset_all_data(self):
        """Completely reset all usage tracking data"""
        # Reset to simplified structure
        self.stats = {
            'total_visits': 0,
            'daily_visits': {},
            'session_data': {},
            'user_agents': {},
            'first_visit': None,
            'last_visit': None,
            'hourly_distribution': {str(i): 0 for i in range(24)},
            'daily_distribution': {str(i): 0 for i in range(7)},
            'monthly_visits': {}
        }
        self._save_stats()
        return True

# Global instance
usage_tracker = UsageTracker()