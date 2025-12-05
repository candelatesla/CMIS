"""
Test refined email generation and actually send via N8N webhook
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from datetime import datetime, timezone, timedelta
from services.student_service import StudentService
from services.mentor_service import MentorService
from services.email_service import EmailService
from ai.email_generation import generate_mentor_outreach_email


def test_generate_and_send_email():
    """Generate a refined email and send it immediately"""
    print("=" * 80)
    print("REFINED EMAIL GENERATION + SEND TEST")
    print("=" * 80)
    print()
    
    # Initialize services
    student_service = StudentService()
    mentor_service = MentorService()
    email_service = EmailService()
    
    # Get a real student
    students = student_service.list_students({"major": "Computer Science"})
    if not students:
        print("❌ No students found")
        return
    
    student = students[0]
    print(f"Selected Student: {student.get('name')}")
    print(f"  Major: {student.get('major')}")
    print(f"  Graduation: {student.get('grad_year')}")
    print(f"  Interests: {', '.join(student.get('interests', [])[:3])}")
    print()
    
    # Get a real mentor
    mentors = mentor_service.list_mentors()
    if not mentors:
        print("❌ No mentors found")
        return
    
    mentor = mentors[0]
    print(f"Selected Mentor: {mentor.get('name')}")
    print(f"  Email: {mentor.get('email')}")
    print(f"  Company: {mentor.get('company')}")
    print(f"  Title: {mentor.get('job_title')}")
    print(f"  Expertise: {', '.join(mentor.get('expertise_areas', [])[:3])}")
    print()
    
    # Create match reason WITHOUT scores
    student_interests = ', '.join(student.get('interests', [])[:2])
    mentor_expertise = ', '.join(mentor.get('expertise_areas', [])[:2])
    
    match_reason = f"{student.get('name')} is passionate about {student_interests}, which aligns well with your expertise in {mentor_expertise}. This mentorship could provide valuable guidance as they prepare for their career in {student.get('major')}."
    
    print("=" * 80)
    print("STEP 1: Generate Refined Email")
    print("=" * 80)
    print()
    
    try:
        subject, body = generate_mentor_outreach_email(student, mentor, match_reason)
        
        print(f"SUBJECT: {subject}")
        print()
        print("BODY:")
        print("-" * 80)
        print(body)
        print("-" * 80)
        print()
        
        # Validate no scores
        has_scores = any(keyword in body.lower() for keyword in ["score", "similarity", "algorithm", "match score", "%"])
        if has_scores:
            print("⚠️  Warning: Score references detected!")
        else:
            print("✅ No score/algorithm references (clean email)")
        
        print()
        
        # STEP 2: Schedule the email to send immediately
        print("=" * 80)
        print("STEP 2: Schedule Email for Immediate Delivery")
        print("=" * 80)
        print()
        
        email_log = email_service.schedule_email(
            recipient_email=mentor.get('email'),
            recipient_role="mentor",
            subject=subject,
            body=body,
            related_match_id=None
        )
        
        email_id = email_log.get("_id")
        planned_time = email_log.get("planned_send_time")
        
        print(f"✅ Email scheduled with ID: {email_id}")
        print(f"   Recipient: {mentor.get('email')}")
        print(f"   Status: {email_log.get('status')}")
        print(f"   Planned Time: {planned_time}")
        print()
        
        # STEP 3: Make it due immediately and send
        print("=" * 80)
        print("STEP 3: Send Email via N8N Webhook")
        print("=" * 80)
        print()
        
        # Update to make due now
        past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        email_service.update_email_log(email_id, {
            "planned_send_time": past_time
        })
        
        print("⏰ Email marked as due for sending...")
        print()
        
        # Send due emails
        results = email_service.send_due_emails()
        
        print("SEND RESULTS:")
        print("-" * 80)
        print(f"  Safe Test Mode: {results.get('safe_test_mode', False)}")
        print(f"  Total Processed: {results.get('total_processed', 0)}")
        print(f"  Successfully Sent: {results.get('sent', 0)}")
        print(f"  Failed: {results.get('failed', 0)}")
        print()
        
        # Show details
        if results.get('details'):
            for detail in results['details']:
                if detail.get('email_id') == email_id:
                    print(f"Email Status: {detail.get('status')}")
                    original = detail.get('original_recipient')
                    redirected = detail.get('redirected_to')
                    
                    if redirected:
                        print(f"  Original Recipient: {original}")
                        print(f"  → Redirected To: {redirected} (Safe Test Mode)")
                    else:
                        print(f"  Sent To: {original}")
                    print()
        
        # Verify final status
        sent_email = email_service.get_email_log_by_id(email_id)
        final_status = sent_email.get('status')
        
        print("=" * 80)
        if final_status == "sent":
            print("✅ EMAIL SUCCESSFULLY SENT")
            print("=" * 80)
            print()
            print("Summary:")
            print(f"  • Refined email generated (no scores/algorithms)")
            print(f"  • Scheduled with human-like timing")
            print(f"  • Delivered via N8N webhook")
            print(f"  • Final Status: {final_status}")
            if results.get('safe_test_mode'):
                print(f"  • Safe Test Mode: Active (redirected to test emails)")
        elif final_status == "failed":
            print("❌ EMAIL FAILED TO SEND")
            print("=" * 80)
            print()
            error = sent_email.get('error_message', 'Unknown error')
            print(f"Error: {error}")
        else:
            print(f"⚠️  EMAIL STATUS: {final_status}")
            print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()


if __name__ == "__main__":
    test_generate_and_send_email()
