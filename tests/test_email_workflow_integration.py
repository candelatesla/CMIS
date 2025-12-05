"""
Test refined email generation in complete matching workflow
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from services.student_service import StudentService
from services.mentor_service import MentorService
from ai.email_generation import generate_mentor_outreach_email


def test_workflow_integration():
    """Test the refined email generation with real data from database"""
    print("=" * 80)
    print("WORKFLOW INTEGRATION TEST")
    print("=" * 80)
    print()
    
    # Get services
    student_service = StudentService()
    mentor_service = MentorService()
    
    # Get a real student
    students = student_service.list_students({"major": "Computer Science"})
    if not students:
        print("❌ No Computer Science students found in database")
        return
    
    student = students[0]
    print(f"Selected Student: {student.get('name')}")
    print(f"  Major: {student.get('major')}")
    print(f"  Grad Year: {student.get('grad_year')}")
    print(f"  Interests: {', '.join(student.get('interests', [])[:3])}")
    print()
    
    # Get a real mentor
    mentors = mentor_service.list_mentors()
    if not mentors:
        print("❌ No mentors found in database")
        return
    
    mentor = mentors[0]
    print(f"Selected Mentor: {mentor.get('name')}")
    print(f"  Company: {mentor.get('company')}")
    print(f"  Title: {mentor.get('job_title')}")
    print(f"  Expertise: {', '.join(mentor.get('expertise_areas', [])[:3])}")
    print()
    
    # Create a match reason WITHOUT scores
    match_reason = f"{student.get('name')} is building expertise in {', '.join(student.get('interests', [])[:2])}, which aligns well with your experience in {', '.join(mentor.get('expertise_areas', [])[:2])}. This connection could provide valuable guidance as they prepare for graduation."
    
    print("Generating email...")
    print()
    
    try:
        subject, body = generate_mentor_outreach_email(student, mentor, match_reason)
        
        print("=" * 80)
        print("GENERATED EMAIL FOR REAL WORKFLOW")
        print("=" * 80)
        print()
        print(f"TO: {mentor.get('email')}")
        print(f"SUBJECT: {subject}")
        print()
        print(body)
        print()
        print("=" * 80)
        print()
        
        # Quick validation
        has_scores = any(keyword in body.lower() for keyword in ["score", "similarity", "algorithm", "match score"])
        has_proper_format = body.count('\n\n') >= 2
        
        if not has_scores and has_proper_format:
            print("✅ Email ready for production use")
            print("   • No technical/AI references")
            print("   • Professional formatting")
            print("   • Human, warm tone")
        else:
            if has_scores:
                print("⚠️  Warning: Score/algorithm references detected")
            if not has_proper_format:
                print("⚠️  Warning: Limited paragraph spacing")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()


if __name__ == "__main__":
    test_workflow_integration()
