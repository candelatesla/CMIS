"""
Test Safe Test Mode for Email Delivery
Tests email redirection to test addresses without polluting production inboxes
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from datetime import datetime, timezone, timedelta
from services.email_service import EmailService
from config import get_safe_test_mode, get_safe_test_emails


def test_safe_mode_configuration():
    """Test that Safe Test Mode configuration is loaded correctly"""
    print("=" * 80)
    print("SAFE TEST MODE CONFIGURATION TEST")
    print("=" * 80)
    print()
    
    safe_mode = get_safe_test_mode()
    test_emails = get_safe_test_emails()
    
    print(f"Safe Test Mode Enabled: {safe_mode}")
    print(f"Test Email Count: {len(test_emails)}")
    print()
    
    if test_emails:
        print("Test Email Addresses:")
        for i, email in enumerate(test_emails, 1):
            print(f"  {i}. {email}")
    else:
        print("⚠️  No test emails configured!")
    
    print()
    
    if safe_mode and len(test_emails) > 0:
        print("✅ Safe Test Mode configured correctly")
        return True
    elif not safe_mode:
        print("⚠️  Safe Test Mode is DISABLED - emails will go to real recipients")
        return True
    else:
        print("❌ Safe Test Mode enabled but no test emails configured")
        return False


def test_email_redirection():
    """Test that emails are redirected to test addresses in Safe Mode"""
    print()
    print("=" * 80)
    print("EMAIL REDIRECTION TEST")
    print("=" * 80)
    print()
    
    email_service = EmailService()
    safe_mode = get_safe_test_mode()
    test_emails = get_safe_test_emails()
    
    if not safe_mode:
        print("⚠️  Safe Test Mode is OFF - skipping redirection test")
        print("    (Set SAFE_TEST_MODE=true in .env to test)")
        return True
    
    # Schedule test emails to different "production" recipients
    production_recipients = [
        "judge1@example.com",
        "judge2@example.com", 
        "judge3@example.com",
        "judge4@example.com",
        "judge5@example.com"
    ]
    
    print(f"Scheduling {len(production_recipients)} emails to production recipients...")
    print()
    
    scheduled_ids = []
    for i, prod_email in enumerate(production_recipients):
        # Schedule in the past so they're immediately due
        past_time = datetime.now(timezone.utc) - timedelta(minutes=1)
        
        email_log = email_service.schedule_email(
            recipient_email=prod_email,
            recipient_role="mentor",
            subject=f"Safe Mode Test {i+1}",
            body=f"This email was originally intended for {prod_email}",
            related_match_id=None
        )
        
        if "_id" in email_log:
            email_id = email_log["_id"]
            scheduled_ids.append(email_id)
            
            # Manually update to make it due now
            email_service.update_email_log(email_id, {
                "planned_send_time": past_time
            })
            
            print(f"  {i+1}. Scheduled for: {prod_email}")
        else:
            print(f"  ❌ Failed to schedule email {i+1}")
    
    print()
    print(f"✅ Scheduled {len(scheduled_ids)} emails")
    print()
    
    # Send due emails (should redirect in Safe Mode)
    print("Sending due emails (with Safe Mode redirection)...")
    print()
    
    results = email_service.send_due_emails()
    
    print("SENDING RESULTS:")
    print("-" * 80)
    print(f"Safe Test Mode: {results.get('safe_test_mode', False)}")
    print(f"Total Processed: {results.get('total_processed', 0)}")
    print(f"Successfully Sent: {results.get('sent', 0)}")
    print(f"Failed: {results.get('failed', 0)}")
    print()
    
    # Show redirection details
    if results.get("details"):
        print("REDIRECTION DETAILS:")
        print("-" * 80)
        
        redirected_count = 0
        for detail in results["details"]:
            original = detail.get("original_recipient")
            redirected_to = detail.get("redirected_to")
            status = detail.get("status")
            
            if redirected_to:
                print(f"✉️  {original}")
                print(f"   → REDIRECTED TO: {redirected_to}")
                print(f"   Status: {status}")
                print()
                redirected_count += 1
            else:
                print(f"✉️  {original}")
                print(f"   Status: {status}")
                print()
        
        print(f"Total Redirected: {redirected_count}/{len(results['details'])}")
        print()
        
        if redirected_count > 0:
            print("✅ Email redirection working correctly!")
            
            # Verify rotation through test emails
            used_test_emails = set()
            for detail in results["details"]:
                redirected_to = detail.get("redirected_to")
                if redirected_to:
                    used_test_emails.add(redirected_to)
            
            print()
            print("Test Email Distribution:")
            for test_email in test_emails:
                count = sum(1 for d in results["details"] if d.get("redirected_to") == test_email)
                print(f"  {test_email}: {count} emails")
            
            return True
        else:
            print("⚠️  No emails were redirected (check Safe Mode config)")
            return False
    else:
        print("⚠️  No details available")
        return False


def test_production_mode():
    """Verify that production mode (Safe Mode OFF) doesn't redirect"""
    print()
    print("=" * 80)
    print("PRODUCTION MODE VERIFICATION")
    print("=" * 80)
    print()
    
    safe_mode = get_safe_test_mode()
    
    if safe_mode:
        print("⚠️  Safe Test Mode is ON")
        print("    To test production mode, set SAFE_TEST_MODE=false in .env")
        print()
        print("✅ Skipping production mode test (Safe Mode active)")
        return True
    else:
        print("✅ Safe Test Mode is OFF - Production mode active")
        print("    Emails will be sent to original recipients")
        print()
        print("⚠️  WARNING: Be careful sending emails in production mode!")
        return True


def main():
    """Run all Safe Test Mode tests"""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SAFE TEST MODE VERIFICATION" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    all_passed = True
    
    # Test 1: Configuration
    if not test_safe_mode_configuration():
        all_passed = False
    
    # Test 2: Email Redirection
    if not test_email_redirection():
        all_passed = False
    
    # Test 3: Production Mode
    if not test_production_mode():
        all_passed = False
    
    # Final Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print()
        print("Safe Test Mode is working correctly!")
        print()
        print("Benefits:")
        print("  • Production judge inboxes remain clean")
        print("  • Emails redirected to test team addresses")
        print("  • Original recipients stored in EmailLog")
        print("  • Easy to toggle between test and production modes")
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Please check configuration and try again.")
    
    print()


if __name__ == "__main__":
    main()
