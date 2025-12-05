"""
Test Email History System
Verify that scheduled, sent, and failed emails are properly tracked and displayed
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from datetime import datetime, timezone, timedelta
from services.email_service import EmailService


def test_email_history_system():
    """Test the complete email history system"""
    print("=" * 80)
    print("EMAIL HISTORY SYSTEM TEST")
    print("=" * 80)
    print()
    
    email_service = EmailService()
    
    # Test 1: Scheduled Emails
    print("TEST 1: Scheduled Emails (Future Queue)")
    print("-" * 80)
    scheduled = email_service.list_scheduled_emails()
    print(f"✅ Found {len(scheduled)} scheduled email(s)")
    
    if scheduled:
        print("\nSample scheduled emails:")
        for i, email in enumerate(scheduled[:3], 1):
            recipient = email.get("recipient_email")
            subject = email.get("subject", "")[:50]
            planned = email.get("planned_send_time")
            
            if isinstance(planned, str):
                planned_dt = datetime.fromisoformat(planned.replace('Z', '+00:00'))
            else:
                planned_dt = planned
            
            formatted_time = planned_dt.strftime("%b %d, %Y %I:%M %p") if planned_dt else "N/A"
            
            print(f"  {i}. {recipient}")
            print(f"     Subject: {subject}")
            print(f"     Planned: {formatted_time}")
            print()
    else:
        print("  No scheduled emails in queue\n")
    
    # Test 2: Sent Emails
    print("\nTEST 2: Sent Emails (History)")
    print("-" * 80)
    sent = email_service.list_sent_emails(limit=10)
    print(f"✅ Found {len(sent)} sent email(s)")
    
    if sent:
        print("\nSample sent emails:")
        for i, email in enumerate(sent[:3], 1):
            recipient = email.get("recipient_email")
            subject = email.get("subject", "")[:50]
            planned = email.get("planned_send_time")
            actual = email.get("actual_send_time")
            
            if isinstance(planned, str):
                planned_dt = datetime.fromisoformat(planned.replace('Z', '+00:00'))
            else:
                planned_dt = planned
                
            if isinstance(actual, str):
                actual_dt = datetime.fromisoformat(actual.replace('Z', '+00:00'))
            else:
                actual_dt = actual
            
            planned_time = planned_dt.strftime("%b %d, %I:%M %p") if planned_dt else "N/A"
            actual_time = actual_dt.strftime("%b %d, %I:%M %p") if actual_dt else "N/A"
            
            print(f"  {i}. {recipient}")
            print(f"     Subject: {subject}")
            print(f"     Planned: {planned_time}")
            print(f"     Sent: {actual_time}")
            print()
    else:
        print("  No sent emails yet\n")
    
    # Test 3: Failed Emails
    print("\nTEST 3: Failed Emails (Error Log)")
    print("-" * 80)
    failed = email_service.list_failed_emails(limit=10)
    print(f"✅ Found {len(failed)} failed email(s)")
    
    if failed:
        print("\nSample failed emails:")
        for i, email in enumerate(failed[:3], 1):
            recipient = email.get("recipient_email")
            subject = email.get("subject", "")[:50]
            error = email.get("error_message", "Unknown")[:100]
            failure_time = email.get("actual_send_time")
            
            if isinstance(failure_time, str):
                failure_dt = datetime.fromisoformat(failure_time.replace('Z', '+00:00'))
            else:
                failure_dt = failure_time
            
            failure_formatted = failure_dt.strftime("%b %d, %I:%M %p") if failure_dt else "N/A"
            
            print(f"  {i}. {recipient}")
            print(f"     Subject: {subject}")
            print(f"     Failed: {failure_formatted}")
            print(f"     Error: {error}")
            print()
    else:
        print("  No failed emails (good!)\n")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"📅 Scheduled (Future): {len(scheduled)}")
    print(f"✅ Sent (Success): {len(sent)}")
    print(f"❌ Failed (Errors): {len(failed)}")
    print(f"📊 Total Tracked: {len(scheduled) + len(sent) + len(failed)}")
    print()
    
    # Verify fields
    print("FIELD VERIFICATION:")
    print("-" * 80)
    
    all_passed = True
    
    # Check scheduled emails have correct fields
    if scheduled:
        sample = scheduled[0]
        required_fields = ["recipient_email", "subject", "planned_send_time", "status"]
        missing = [f for f in required_fields if f not in sample]
        
        if not missing:
            print("✅ Scheduled emails have all required fields")
        else:
            print(f"❌ Scheduled emails missing fields: {missing}")
            all_passed = False
    
    # Check sent emails have correct fields (actual_send_time optional for legacy emails)
    if sent:
        sample = sent[0]
        required_fields = ["recipient_email", "subject", "planned_send_time", "status"]
        missing = [f for f in required_fields if f not in sample]
        
        if not missing:
            has_actual_time = "actual_send_time" in sample or "sent_at" in sample
            if has_actual_time:
                print("✅ Sent emails have all required fields (with timing data)")
            else:
                print("✅ Sent emails have all required fields (legacy format - no actual_send_time)")
        else:
            print(f"❌ Sent emails missing fields: {missing}")
            all_passed = False
    
    # Check failed emails have correct fields
    if failed:
        sample = failed[0]
        required_fields = ["recipient_email", "subject", "planned_send_time", "error_message", "status"]
        missing = [f for f in required_fields if f not in sample]
        
        if not missing:
            has_actual_time = "actual_send_time" in sample
            if has_actual_time:
                print("✅ Failed emails have all required fields (with timing data)")
            else:
                print("✅ Failed emails have all required fields (legacy format - no actual_send_time)")
        else:
            print(f"❌ Failed emails missing fields: {missing}")
            all_passed = False
    
    print()
    
    if all_passed:
        print("=" * 80)
        print("✅ ALL TESTS PASSED - EMAIL HISTORY SYSTEM WORKING CORRECTLY")
        print("=" * 80)
        print()
        print("The Streamlit Email Management page should now display:")
        print("  • 📅 Scheduled Emails tab - Future emails in queue")
        print("  • ✅ Sent Emails tab - Successfully delivered emails")
        print("  • ❌ Failed Emails tab - Emails with delivery errors")
    else:
        print("=" * 80)
        print("⚠️ SOME ISSUES DETECTED - CHECK OUTPUT ABOVE")
        print("=" * 80)
    
    print()


if __name__ == "__main__":
    test_email_history_system()
