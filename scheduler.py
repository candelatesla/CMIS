"""
Scheduler module for automated tasks
Uses APScheduler for running background jobs
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime


class TaskScheduler:
    """Scheduler for automated tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._is_running = False
    
    def start(self):
        """Start the scheduler"""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            print("Task scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            print("Task scheduler stopped")
    
    def add_daily_task(self, func, hour: int = 9, minute: int = 0):
        """
        Add a daily scheduled task
        
        Args:
            func: Function to execute
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
        """
        trigger = CronTrigger(hour=hour, minute=minute)
        self.scheduler.add_job(func, trigger)
        print(f"Added daily task: {func.__name__} at {hour:02d}:{minute:02d}")
    
    def add_weekly_task(self, func, day_of_week: int = 0, hour: int = 9, minute: int = 0):
        """
        Add a weekly scheduled task
        
        Args:
            func: Function to execute
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
        """
        trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
        self.scheduler.add_job(func, trigger)
        print(f"Added weekly task: {func.__name__}")
    
    def add_interval_task(self, func, minutes: int = 60):
        """
        Add a task that runs at fixed intervals
        
        Args:
            func: Function to execute
            minutes: Interval in minutes
        """
        self.scheduler.add_job(func, 'interval', minutes=minutes)
        print(f"Added interval task: {func.__name__} every {minutes} minutes")
    
    def setup_email_sender(self):
        """
        Set up the automatic email sender that runs every minute.
        This checks for scheduled emails that are due and sends them via N8N webhook.
        """
        from services.email_service import EmailService
        
        def send_emails_job():
            """Job to send due emails"""
            try:
                email_service = EmailService()
                results = email_service.send_due_emails()
                
                if results["total_processed"] > 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Email sender: "
                          f"Processed {results['total_processed']}, "
                          f"Sent {results['sent']}, "
                          f"Failed {results['failed']}")
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Email sender error: {str(e)}")
        
        # Run every minute
        self.scheduler.add_job(send_emails_job, 'interval', minutes=1)
        print("Email sender scheduled: Runs every 1 minute")


# Global scheduler instance
scheduler = TaskScheduler()


# Initialize email sender on import
def init_scheduler():
    """Initialize and start the scheduler with email sender"""
    scheduler.setup_email_sender()
    scheduler.start()
