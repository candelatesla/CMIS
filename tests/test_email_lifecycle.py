"""
Test complete email lifecycle with proper field tracking
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from datetime import datetime, timezone, timedelta
from services.email_service import EmailService


def test_complete_email_lifecycle():
    """Test scheduling, sending, and tracking a complete email lifecycle"""
    print("=" * 80)
    print("COMPLETE EMAIL LIFECYCLE TEST")
    print("=" * 80)
    print()
    
    email_service = EmailService()
    
    # STEP 1: Schedule an email
    print("STEP 1: Scheduling a new email...")
    print("-" * 80)
    
    email_log = email_service.schedule_email(
        recipient_email="lifecycle-test@example.com",
        recipient_role="mentor",
        subject="Lifecycle Test Email",
        body="Testing complete email tracking with all fields",
        related_match_id=None
    )
    
    email_id = email_log.get("_id")
    print(f"✅ Email scheduled with ID: {email_id}")
    print(f"   Status: {email_log.get('status')}")
    print(f"   Planned Time: {email_log.get('planned_send_time')}")
    print(f"   Created At: {email_log.get('created_at')}")
    print()
    
    # Verify fields
    required_fields = ["recipient_email", "subject", "body", "status", "planned_send_time", "created_at"]
    missing = [f for f in required_fields if f not in email_log]
    
    if not missing:
        print("✅ All required fields present in scheduled email")
    else:
        print(f"❌ Missing fields: {missing}")
    
    print()
    
    # STEP 2: Make it due immediately and send it
    print("STEP 2: Making email due and sending...")
    print("-" * 80)
    
    # Update to make it due now
    past_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    email_service.update_email_log(email_id, {
        "planned_send_time": past_time
    })
    
    print("✅ Email marked as due")
    print()
    
    # Send due emails
    results = email_service.send_due_emails()
    
    print(f"Send Results:")
    print(f"  Total Processed: {results.get('total_processed', 0)}")
    print(f"  Sent: {results.get('sent', 0)}")
    print(f"  Failed: {results.get('failed', 0)}")
    print(f"  Safe Test Mode: {results.get('safe_test_mode', False)}")
    print()
    
    # STEP 3: Retrieve and verify the sent email
    print("STEP 3: Verifying sent email record...")
    print("-" * 80)
    
    sent_email = email_service.get_email_log_by_id(email_id)
    
    if sent_email:
        print(f"Status: {sent_email.get('status')}")
        print(f"Recipient: {sent_email.get('recipient_email')}")
        print(f"Subject: {sent_email.get('subject')}")
        print(f"Planned Time: {sent_email.get('planned_send_time')}")
        print(f"Actual Send Time: {sent_email.get('actual_send_time')}")
        print(f"Created At: {sent_email.get('created_at')}")
        print()
        
        # Verify all tracking fields
        tracking_fields = {
            "status": sent_email.get("status"),
            "actual_send_time": sent_email.get("actual_send_time"),
            "planned_send_time": sent_email.get("planned_send_time"),
            "created_at": sent_email.get("created_at")
        }
        
        if all(tracking_fields.values()):
            print("✅ ALL TRACKING FIELDS PRESENT:")
            for field, value in tracking_fields.items():
                print(f"   • {field}: {value}")
        else:
            print("❌ MISSING TRACKING FIELDS:")
            for field, value in tracking_fields.items():
                status = "✅" if value else "❌"
                print(f"   {status} {field}: {value}")
    else:
        print("❌ Could not retrieve sent email")
    
    print()
    print("=" * 80)
    print("LIFECYCLE TEST COMPLETE")
    print("=" * 80)
    print()
    
    if sent_email and sent_email.get("status") == "sent" and sent_email.get("actual_send_time"):
        print("✅ SUCCESS: Email lifecycle tracked correctly!")
        print()
        print("New emails will have:")
        print("  • created_at: When email was first scheduled")
        print("  • planned_send_time: When email should be sent")
        print("  • actual_send_time: When email was actually delivered")
        print("  • status: scheduled → sent (or failed)")
        return True
    else:
        print("⚠️ Some issues detected in lifecycle tracking")
        return False


if __name__ == "__main__":
    test_complete_email_lifecycle()
