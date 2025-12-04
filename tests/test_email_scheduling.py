"""
Test script for email scheduling and sending functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.email_service import EmailService
from datetime import datetime, timezone

print("=" * 80)
print("TESTING: Email Scheduling & Sending")
print("=" * 80)
print()

email_service = EmailService()

# Test 1: Schedule an email
print("Test 1: Scheduling an email...")
print("-" * 80)

scheduled_email = email_service.schedule_email(
    recipient_email="mentor@example.com",
    recipient_role="mentor",
    subject="Mentorship Opportunity: Sarah Chen",
    body="Hi Mentor,\n\nWe'd like to connect you with Sarah Chen...\n\nBest regards,\nThe CMIS Team",
    related_match_id="test_match_123"
)

if "error" not in scheduled_email:
    print(f"✅ Email scheduled successfully!")
    print(f"   Email ID: {scheduled_email.get('_id')}")
    print(f"   Recipient: {scheduled_email.get('recipient_email')}")
    print(f"   Status: {scheduled_email.get('status')}")
    
    # Parse the scheduled time
    scheduled_time = scheduled_email.get('planned_send_time')
    if isinstance(scheduled_time, str):
        from dateutil import parser
        scheduled_time = parser.parse(scheduled_time)
    
    # Ensure timezone aware
    if scheduled_time.tzinfo is None:
        scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    delay = (scheduled_time - now).total_seconds() / 60
    
    print(f"   Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"   Delay: ~{delay:.1f} minutes from now")
else:
    print(f"❌ Error: {scheduled_email.get('error')}")

print()

# Test 2: Check for due emails (should be none if delay > 15 minutes)
print("Test 2: Checking for due emails...")
print("-" * 80)

results = email_service.send_due_emails()
print(f"Total processed: {results['total_processed']}")
print(f"Sent: {results['sent']}")
print(f"Failed: {results['failed']}")

if results['total_processed'] == 0:
    print("✅ No emails due yet (as expected with 15min+ delay)")
else:
    print(f"📧 Processed {results['total_processed']} due email(s)")
    for detail in results['details']:
        print(f"   - {detail['recipient']}: {detail['status']}")

print()

# Test 3: Check scheduled emails in database
print("Test 3: Listing scheduled emails...")
print("-" * 80)

scheduled_emails = email_service.list_email_logs({"status": "scheduled"})
print(f"Found {len(scheduled_emails)} scheduled email(s) in database")

for email in scheduled_emails[:3]:  # Show first 3
    print(f"   - {email.get('recipient_email')}: {email.get('subject')[:50]}")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print()
print("Note: To test actual sending:")
print("  1. Manually update an email's 'planned_send_time' to the past")
print("  2. Run send_due_emails() again")
print("  3. Or wait for the scheduler to process it automatically")
