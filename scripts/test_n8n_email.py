"""
Standalone N8N Email Sending Test Script

Purpose: Test that n8n email delivery works
Does NOT interact with database, services, or any other project code
"""
import requests


# N8N Webhook URL
N8N_WEBHOOK = "https://khushishah.app.n8n.cloud/webhook/match-mentor"


def send_test_email(to_email, subject, body):
    """
    Send a test email via N8N webhook
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body content
    """
    payload = {
        "email": to_email,
        "subject": subject,
        "body": body
    }
    
    print(f"Sending to: {to_email}")
    print(f"Subject: {subject}")
    
    try:
        response = requests.post(N8N_WEBHOOK, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Email sent successfully!\n")
        else:
            print("❌ Email failed to send\n")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")


if __name__ == "__main__":
    print("=" * 80)
    print("N8N EMAIL DELIVERY TEST")
    print("=" * 80)
    print(f"Webhook URL: {N8N_WEBHOOK}")
    print()
    
    # Test recipients
    recipients = [
        "yash.doshi@tamu.edu",
        "khushi.shah@tamu.edu",
        "ujjawal.patel@tamu.edu",
        "chintan.shah@tamu.edu"
    ]
    
    # Send test email to each recipient
    for recipient in recipients:
        send_test_email(
            to_email=recipient,
            subject="We have good news!",
            body="This is a test email to confirm that the CMIS n8n workflow is working correctly."
        )
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Sent {len(recipients)} test emails")
    print("Check inboxes for:")
    for r in recipients:
        print(f"  - {r}")
