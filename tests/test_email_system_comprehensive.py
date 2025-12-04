"""
Comprehensive test of the full email workflow:
1. Schedule email with human-like timing
2. Verify scheduler setup
3. Show webhook configuration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.email_service import EmailService
from scheduler import scheduler
from config import N8N_WEBHOOK_URL
from datetime import datetime

print("=" * 80)
print("CMIS EMAIL SYSTEM - COMPREHENSIVE TEST")
print("=" * 80)
print()

# Test 1: Configuration
print("✓ Configuration Check")
print("-" * 80)
print(f"N8N Webhook URL: {N8N_WEBHOOK_URL}")
print(f"Webhook configured: {'✅ Yes' if N8N_WEBHOOK_URL else '❌ No'}")
print()

# Test 2: Schedule an email
print("✓ Scheduling Email")
print("-" * 80)
email_service = EmailService()

scheduled = email_service.schedule_email(
    recipient_email="khushi.shah@example.com",
    recipient_role="student",
    subject="Welcome to CMIS Mentorship Program",
    body="""Hi Khushi,

Welcome to the CMIS Mentorship Program! We're excited to have you join us.

Your profile has been created, and we'll be matching you with a mentor soon based on your interests and skills.

Best regards,
The CMIS Team""",
    related_match_id=None
)

if "error" not in scheduled:
    scheduled_time = scheduled.get('planned_send_time')
    if isinstance(scheduled_time, str):
        from dateutil import parser
        scheduled_time = parser.parse(scheduled_time)
    
    print(f"✅ Email scheduled successfully!")
    print(f"   ID: {scheduled.get('_id')}")
    print(f"   To: {scheduled.get('recipient_email')}")
    print(f"   Subject: {scheduled.get('subject')}")
    print(f"   Status: {scheduled.get('status')}")
    print(f"   Will send at: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
else:
    print(f"❌ Error: {scheduled.get('error')}")

print()

# Test 3: Scheduler setup
print("✓ Scheduler Configuration")
print("-" * 80)
print("Setting up email sender job...")
scheduler.setup_email_sender()
print("✅ Email sender configured to run every 1 minute")
print()

# Test 4: Current scheduled emails
print("✓ Current Scheduled Emails")
print("-" * 80)
scheduled_emails = email_service.list_email_logs({"status": "scheduled"})
print(f"Total scheduled emails waiting: {len(scheduled_emails)}")

if scheduled_emails:
    print("\nUpcoming emails:")
    for i, email in enumerate(scheduled_emails[:5], 1):
        send_time = email.get('planned_send_time')
        if isinstance(send_time, str):
            from dateutil import parser
            send_time = parser.parse(send_time)
        print(f"   {i}. To: {email.get('recipient_email')}")
        print(f"      Subject: {email.get('subject')[:50]}...")
        print(f"      Scheduled: {send_time.strftime('%Y-%m-%d %H:%M:%S')}")

print()

# Test 5: How it works
print("=" * 80)
print("HOW THE EMAIL SYSTEM WORKS")
print("=" * 80)
print("""
1. SCHEDULING:
   - Call email_service.schedule_email() with recipient and content
   - System computes random send time (15 min - 24 hrs in future)
   - Email stored in MongoDB with status="scheduled"
   
2. AUTOMATIC SENDING:
   - Scheduler runs send_due_emails() every 1 minute
   - Queries all emails with status="scheduled" and time <= now
   - For each email:
     * POST to N8N webhook: https://khushishah.app.n8n.cloud/webhook/match-mentor-2
     * Payload: {"email": "...", "subject": "...", "body": "..."}
     * Success → status="sent"
     * Failure → status="failed" with error message

3. INTEGRATION POINTS:
   - generate_mentor_outreach_email() → creates email content
   - schedule_email() → stores for delayed sending
   - Scheduler → automatically sends when due
   - N8N webhook → actual email delivery (SMTP, etc.)
""")

print("=" * 80)
print("SYSTEM READY")
print("=" * 80)
print()
print("To start the scheduler in your app:")
print("  from scheduler import init_scheduler")
print("  init_scheduler()  # Call this once when app starts")
