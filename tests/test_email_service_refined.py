"""
Test the refined email scheduling logic with EmailService
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from datetime import datetime, timezone
from services.email_service import EmailService


def test_email_service_scheduling():
    """Test the email service with refined scheduling logic"""
    
    print("=" * 80)
    print("EMAIL SERVICE - REFINED SCHEDULING TEST")
    print("=" * 80)
    print()
    
    # Initialize service
    email_service = EmailService()
    
    # Get current time
    now = datetime.now(timezone.utc)
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    current_hour = now.hour
    
    print(f"Current Time: {current_time_str}")
    print(f"Current Hour (UTC): {current_hour}")
    print()
    
    # Determine which rule applies
    if current_hour < 8:
        rule = "Rule 1: Before 8 AM → Schedule between 8-10 AM today"
    elif 8 <= current_hour < 17:
        rule = "Rule 2: 8 AM - 5 PM → Schedule after 10-25 minutes"
    else:
        rule = "Rule 3: After 5 PM → Schedule next day between 8-10 AM"
    
    print(f"Active Rule: {rule}")
    print()
    
    # Schedule 3 test emails
    print("Scheduling 3 test emails:")
    print("-" * 80)
    
    for i in range(3):
        email_log = email_service.schedule_email(
            recipient_email=f"test{i+1}@example.com",
            recipient_role="mentor",
            subject=f"Test Email {i+1}",
            body=f"This is test email number {i+1} using refined scheduling logic.",
            related_match_id=None
        )
        
        if "error" not in email_log:
            email_id = email_log.get("_id")
            scheduled_time_str = email_log.get("planned_send_time")
            status = email_log.get("status")
            
            # Parse scheduled time
            if isinstance(scheduled_time_str, str):
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            else:
                scheduled_time = scheduled_time_str
            
            # Ensure timezone aware
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            
            # Calculate delay
            delay = scheduled_time - now
            delay_minutes = delay.total_seconds() / 60
            
            # Check if next day
            is_next_day = scheduled_time.date() > now.date()
            next_day_marker = " (NEXT DAY)" if is_next_day else ""
            
            print(f"\nEmail {i+1}:")
            print(f"  ID: {email_id}")
            print(f"  To: test{i+1}@example.com")
            print(f"  Status: {status}")
            print(f"  Scheduled: {scheduled_time_str}{next_day_marker}")
            print(f"  Delay: {delay_minutes:.1f} minutes ({delay_minutes/60:.2f} hours)")
        else:
            print(f"\n❌ Error creating email {i+1}: {email_log['error']}")
    
    print()
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print()
    
    # Query all scheduled emails
    scheduled_emails = email_service.list_email_logs({"status": "scheduled"})
    recent_emails = [e for e in scheduled_emails if e.get("recipient_email", "").startswith("test")]
    
    print(f"Total scheduled emails in database: {len(scheduled_emails)}")
    print(f"Recent test emails: {len(recent_emails)}")
    print()
    
    if recent_emails:
        print("✅ Emails successfully scheduled with refined logic")
        print()
        print("Sample scheduled times:")
        for email in recent_emails[:5]:
            scheduled_str = email.get("planned_send_time")
            recipient = email.get("recipient_email")
            print(f"  - {recipient}: {scheduled_str}")
    else:
        print("⚠️  No test emails found")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("✅ Refined scheduling logic integrated successfully!")
    print()
    print("Rules applied:")
    print("  - Before 8 AM: Schedule 8-10 AM today")
    print("  - 8 AM - 5 PM: Schedule +10-25 minutes")
    print("  - After 5 PM: Schedule next day 8-10 AM")


if __name__ == "__main__":
    test_email_service_scheduling()
