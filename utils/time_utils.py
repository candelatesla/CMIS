"""
Time and date utilities
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


class TimeUtils:
    """Utility class for time and date operations"""
    
    @staticmethod
    def get_current_utc() -> datetime:
        """
        Get current UTC datetime
        
        Returns:
            datetime: Current UTC datetime
        """
        return datetime.now(timezone.utc)
    
    @staticmethod
    def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format datetime to string
        
        Args:
            dt: Datetime object
            format_string: Format string
            
        Returns:
            str: Formatted datetime string
        """
        return dt.strftime(format_string)
    
    @staticmethod
    def format_date(dt: datetime) -> str:
        """
        Format datetime to date string (YYYY-MM-DD)
        
        Args:
            dt: Datetime object
            
        Returns:
            str: Formatted date string
        """
        return dt.strftime("%Y-%m-%d")
    
    @staticmethod
    def format_time(dt: datetime) -> str:
        """
        Format datetime to time string (HH:MM:SS)
        
        Args:
            dt: Datetime object
            
        Returns:
            str: Formatted time string
        """
        return dt.strftime("%H:%M:%S")
    
    @staticmethod
    def parse_datetime(date_string: str, format_string: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        """
        Parse string to datetime
        
        Args:
            date_string: Date string to parse
            format_string: Format string
            
        Returns:
            datetime or None: Parsed datetime or None if error
        """
        try:
            return datetime.strptime(date_string, format_string)
        except Exception as e:
            print(f"Error parsing datetime: {str(e)}")
            return None
    
    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """
        Add days to a datetime
        
        Args:
            dt: Datetime object
            days: Number of days to add (can be negative)
            
        Returns:
            datetime: New datetime
        """
        return dt + timedelta(days=days)
    
    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """
        Add hours to a datetime
        
        Args:
            dt: Datetime object
            hours: Number of hours to add (can be negative)
            
        Returns:
            datetime: New datetime
        """
        return dt + timedelta(hours=hours)
    
    @staticmethod
    def days_until(target_date: datetime) -> int:
        """
        Calculate days until a target date
        
        Args:
            target_date: Target datetime
            
        Returns:
            int: Number of days until target (negative if past)
        """
        now = datetime.now(timezone.utc)
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=timezone.utc)
        delta = target_date - now
        return delta.days
    
    @staticmethod
    def is_past(dt: datetime) -> bool:
        """
        Check if a datetime is in the past
        
        Args:
            dt: Datetime to check
            
        Returns:
            bool: True if in the past
        """
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt < now
    
    @staticmethod
    def is_future(dt: datetime) -> bool:
        """
        Check if a datetime is in the future
        
        Args:
            dt: Datetime to check
            
        Returns:
            bool: True if in the future
        """
        return not TimeUtils.is_past(dt)
    
    @staticmethod
    def human_readable_time_diff(dt: datetime) -> str:
        """
        Get human-readable time difference from now
        
        Args:
            dt: Datetime to compare
            
        Returns:
            str: Human-readable time difference (e.g., "2 days ago", "in 3 hours")
        """
        now = datetime.now(timezone.utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        delta = dt - now
        seconds = delta.total_seconds()
        
        if seconds < 0:
            # Past
            seconds = abs(seconds)
            if seconds < 60:
                return "just now"
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            else:
                days = int(seconds / 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            # Future
            if seconds < 60:
                return "in a moment"
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f"in {minutes} minute{'s' if minutes != 1 else ''}"
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f"in {hours} hour{'s' if hours != 1 else ''}"
            else:
                days = int(seconds / 86400)
                return f"in {days} day{'s' if days != 1 else ''}"
    
    @staticmethod
    def get_week_range(dt: Optional[datetime] = None) -> tuple[datetime, datetime]:
        """
        Get the start and end of the week for a given date
        
        Args:
            dt: Datetime (defaults to now)
            
        Returns:
            tuple: (week_start, week_end)
        """
        if dt is None:
            dt = datetime.now(timezone.utc)
        
        week_start = dt - timedelta(days=dt.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        return week_start, week_end


def get_human_like_schedule_time() -> datetime:
    """
    Calculate a human-like scheduled time for email sending based on current time.
    
    Rules:
    - If current time < 8:00 AM: Schedule between 8:00-10:00 AM today
    - If time is 8:00 AM to 5:00 PM: Schedule after 10-25 minutes
    - If time > 5:00 PM: Schedule next day between 8:00-10:00 AM
    
    All times include random minute and second offsets for human-like scheduling.
    
    Returns:
        datetime: Scheduled time in UTC with human-like randomization
    """
    import random
    
    now = datetime.now(timezone.utc)
    
    # Get current hour (in UTC)
    current_hour = now.hour
    
    # Rule 1: If before 8:00 AM - schedule between 8:00-10:00 AM today
    if current_hour < 8:
        # Random time between 8:00 and 10:00 AM today
        target_hour = random.randint(8, 9)  # 8 or 9 (10 AM would be start of next hour)
        target_minute = random.randint(0, 59)
        target_second = random.randint(0, 59)
        
        scheduled_time = now.replace(
            hour=target_hour,
            minute=target_minute,
            second=target_second,
            microsecond=0
        )
    
    # Rule 2: If between 8:00 AM and 5:00 PM - schedule after 10-25 minutes
    elif 8 <= current_hour < 17:  # 8 AM to 5 PM (17:00)
        # Random delay between 10 and 25 minutes
        delay_minutes = random.randint(10, 25)
        scheduled_time = now + timedelta(minutes=delay_minutes)
        
        # Add random seconds for human-like timing
        random_seconds = random.randint(0, 59)
        scheduled_time = scheduled_time.replace(second=random_seconds, microsecond=0)
    
    # Rule 3: If after 5:00 PM - schedule next day between 8:00-10:00 AM
    else:  # current_hour >= 17 (after 5 PM)
        # Schedule for next day
        next_day = now + timedelta(days=1)
        
        # Random time between 8:00 and 10:00 AM
        target_hour = random.randint(8, 9)
        target_minute = random.randint(0, 59)
        target_second = random.randint(0, 59)
        
        scheduled_time = next_day.replace(
            hour=target_hour,
            minute=target_minute,
            second=target_second,
            microsecond=0
        )
    
    return scheduled_time
