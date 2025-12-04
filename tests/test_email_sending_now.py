"""
Test sending a due email immediately via N8N webhook
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.email_service import EmailService
from datetime import datetime, timezone, timedelta

print("=" * 80)
print("TESTING: Immediate Email Sending via N8N")
print("=" * 80)
print()

email_service = EmailService()

# Create an email that's due now (in the past)
print("Creating an email scheduled 1 minute in the past...")
print("-" * 80)

past_time = datetime.now(timezone.utc) - timedelta(minutes=1)

email_data = {
    "recipient_email": "test@example.com",
    "recipient_role": "mentor",
    "subject": "Test Email from CMIS",
    "body": "This is a test email sent via N8N webhook.\n\nBest regards,\nThe CMIS Team",
    "status": "scheduled",
    "planned_send_time": past_time,
    "created_at": past_time,
    "updated_at": past_time
}

created_email = email_service.create_email_log(email_data)

if "error" not in created_email:
    print(f"✅ Email created with ID: {created_email.get('_id')}")
    print(f"   Scheduled for: {past_time.strftime('%Y-%m-%d %H:%M:%S UTC')} (in the past)")
else:
    print(f"❌ Error creating email: {created_email.get('error')}")
    exit(1)

print()

# Now send due emails
print("Sending due emails...")
print("-" * 80)

results = email_service.send_due_emails()

print(f"📊 Results:")
print(f"   Total processed: {results['total_processed']}")
print(f"   Successfully sent: {results['sent']}")
print(f"   Failed: {results['failed']}")
print()

if results['details']:
    print("Details:")
    for detail in results['details']:
        status_emoji = "✅" if detail['status'] == 'sent' else "❌"
        print(f"   {status_emoji} {detail['recipient']}: {detail['status']}")
        if 'error' in detail:
            print(f"      Error: {detail['error']}")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
