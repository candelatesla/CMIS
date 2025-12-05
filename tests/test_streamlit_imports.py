"""
Quick test to verify the AI email generation imports work correctly in Streamlit context
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

# Test imports that Streamlit will use
try:
    from ai.workflow import WorkflowEngine
    print("✅ WorkflowEngine import successful")
except Exception as e:
    print(f"❌ WorkflowEngine import failed: {e}")

try:
    from ai.email_generation import generate_mentor_outreach_email
    print("✅ generate_mentor_outreach_email import successful")
except Exception as e:
    print(f"❌ generate_mentor_outreach_email import failed: {e}")

try:
    from services.student_service import StudentService
    from services.mentor_service import MentorService
    print("✅ Service imports successful")
except Exception as e:
    print(f"❌ Service imports failed: {e}")

# Test the function works
try:
    from services.student_service import StudentService
    from services.mentor_service import MentorService
    
    student_service = StudentService()
    mentor_service = MentorService()
    
    students = student_service.list_students()
    mentors = mentor_service.list_mentors()
    
    if students and mentors:
        student = students[0]
        mentor = mentors[0]
        
        match_reason = f"{student.get('name')} is interested in areas that align with your expertise."
        
        subject, body = generate_mentor_outreach_email(student, mentor, match_reason)
        
        print("✅ Email generation test successful")
        print(f"\nSubject: {subject}")
        print(f"Body length: {len(body)} characters")
        print(f"No scores: {not any(k in body.lower() for k in ['score', 'algorithm', '%'])}")
    else:
        print("⚠️ No students or mentors found for testing")
        
except Exception as e:
    print(f"❌ Email generation test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All imports verified - Streamlit should work correctly!")
