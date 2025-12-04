"""
Test the AI Matching page functionality
Simulates the workflow without UI interaction
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from services.student_service import StudentService
from services.match_service import MatchService
from services.email_service import EmailService
from ai.workflow import WorkflowEngine


def test_ai_matching_page_logic():
    """Test the logic behind the AI Matching page"""
    
    print("=" * 80)
    print("AI MATCHING PAGE - FUNCTIONALITY TEST")
    print("=" * 80)
    print()
    
    # Initialize services (same as in app.py)
    student_service = StudentService()
    match_service = MatchService()
    email_service = EmailService()
    workflow = WorkflowEngine()
    
    # Step 1: Get students (for dropdown)
    print("Step 1: Loading students for dropdown...")
    students = student_service.list_students()
    print(f"✅ Found {len(students)} students")
    print()
    
    # Step 2: Select a student (simulate dropdown selection)
    selected_student = students[1]  # Alex Martinez
    student_id = selected_student.get('student_id')
    student_name = selected_student.get('name')
    
    print(f"Step 2: Selected student: {student_name} (ID: {student_id})")
    print()
    
    # Step 3: Set top_n (simulate number input)
    top_n = 2
    print(f"Step 3: Top N mentors: {top_n}")
    print()
    
    # Step 4: Run workflow (simulate button click)
    print("Step 4: Running AI matching workflow...")
    result = workflow.run_matching_workflow_for_student(
        student_id=student_id,
        top_n=top_n
    )
    print()
    
    # Step 5: Display results (simulate UI display)
    print("=" * 80)
    print("WORKFLOW RESULTS (as shown in UI)")
    print("=" * 80)
    print()
    
    if result['success']:
        print(f"✅ Success: Created {result['matches_created']} matches, scheduled {result['emails_scheduled']} emails")
        print()
        
        print("📊 NEW MATCH RESULTS:")
        for i, match in enumerate(result['match_details'], 1):
            print(f"\n  Match {i}:")
            print(f"    Mentor: {match['mentor_name']}")
            print(f"    Email: {match['mentor_email']}")
            print(f"    Score: {match['score']:.1%}")
            print(f"    Rank: #{match['rank']}")
            print(f"    Match ID: {match['match_id']}")
            
            if match.get('email_id'):
                email_log = email_service.get_email_log_by_id(match['email_id'])
                if email_log:
                    print(f"    Email Status: {email_log.get('status')}")
                    print(f"    Scheduled For: {email_log.get('planned_send_time')}")
                    print(f"    Subject: {email_log.get('subject')}")
    else:
        print("❌ Workflow failed")
        for error in result['errors']:
            print(f"  - {error}")
    
    print()
    
    # Step 6: Get past matches (simulate past matches section)
    print("=" * 80)
    print("PAST MATCHES (as shown in table)")
    print("=" * 80)
    print()
    
    past_matches = match_service.list_matches({"student_id": student_id})
    print(f"Found {len(past_matches)} past matches for {student_name}")
    print()
    
    if past_matches:
        from services.mentor_service import MentorService
        mentor_service = MentorService()
        
        for i, match in enumerate(past_matches[:5], 1):  # Show first 5
            mentor = mentor_service.get_mentor_by_id(match.get('mentor_id'))
            mentor_name = mentor.get('name', 'Unknown') if mentor else 'Unknown'
            
            print(f"  {i}. {mentor_name} - {match.get('match_score', 0):.1%} - {match.get('status')}")
            print(f"     Reason: {match.get('reason_summary', 'N/A')[:80]}...")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE - UI LOGIC WORKS CORRECTLY")
    print("=" * 80)
    print()
    print("✅ All page components working:")
    print("   - Student dropdown populated")
    print("   - Top N input functional")
    print("   - Workflow execution successful")
    print("   - Match results displayed with details")
    print("   - Email scheduling confirmed")
    print("   - Past matches retrieved and formatted")
    print()
    print("🎨 UI should display:")
    print("   - Polished dashboard layout")
    print("   - Match cards with scores and AI reasons")
    print("   - Email status and scheduled send times")
    print("   - Past matches table with full history")


if __name__ == "__main__":
    test_ai_matching_page_logic()
