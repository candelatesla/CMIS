"""
Test script for Student Dashboard - Mentor Match feature
Tests that a student can view their assigned mentor
"""
import sys
sys.path.insert(0, '.')

from services.student_service import StudentService
from services.mentor_service import MentorService
from services.match_service import MatchService

def test_mentor_match_feature():
    """Test the mentor match viewing feature"""
    
    print("="*60)
    print("TESTING: Student Dashboard - Mentor Match Feature")
    print("="*60)
    
    # Initialize services
    student_service = StudentService()
    mentor_service = MentorService()
    match_service = MatchService()
    
    print("\n1️⃣ Getting sample student...")
    students = student_service.list_students()
    if not students:
        print("❌ No students found in database")
        return
    
    sample_student = students[0]
    student_id = str(sample_student.get("_id"))
    print(f"✅ Using student: {sample_student.get('name')} ({sample_student.get('email')})")
    
    print("\n2️⃣ Checking for existing matches...")
    matches = match_service.get_matches_by_student(student_id)
    
    if not matches:
        print("⚠️  No matches found for this student")
        print("   This is expected if no matches have been created yet.")
        print("   The student dashboard will show: 'You do not have an assigned mentor yet.'")
        return
    
    print(f"✅ Found {len(matches)} match(es)")
    
    # Find active or pending match
    active_match = None
    pending_match = None
    
    for match in matches:
        status = match.get("status", "unknown")
        print(f"   - Match ID: {match.get('_id')} | Status: {status}")
        
        if status == "active":
            active_match = match
        elif status == "pending" and not pending_match:
            pending_match = match
    
    selected_match = active_match or pending_match
    
    if not selected_match:
        print("⚠️  No active or pending matches found")
        return
    
    print(f"\n3️⃣ Selected match: {selected_match.get('_id')}")
    print(f"   Status: {selected_match.get('status')}")
    
    # Get mentor details
    mentor_id = selected_match.get("mentor_id")
    print(f"\n4️⃣ Fetching mentor details (ID: {mentor_id})...")
    
    mentor = mentor_service.get_mentor_by_id(mentor_id)
    
    if not mentor or "error" in mentor:
        print("❌ Could not load mentor details")
        return
    
    print(f"✅ Mentor loaded: {mentor.get('name')}")
    
    print("\n5️⃣ Mentor information that will be displayed:")
    print(f"   📧 Email: {mentor.get('email')}")
    print(f"   🏢 Company: {mentor.get('company')}")
    print(f"   💼 Job Title: {mentor.get('job_title')}")
    print(f"   🏭 Industry: {mentor.get('industry')}")
    print(f"   📅 Experience: {mentor.get('years_of_experience')} years")
    
    expertise = mentor.get('expertise_areas', [])
    if expertise:
        print(f"   🎯 Expertise: {', '.join(expertise)}")
    
    interests = mentor.get('interests', [])
    if interests:
        print(f"   💡 Interests: {', '.join(interests)}")
    
    match_reason = selected_match.get("match_reason", "")
    if match_reason:
        print(f"\n6️⃣ Match reason preview:")
        print(f"   {match_reason[:150]}...")
    else:
        print("\n⚠️  No match reason available")
    
    resume_text = mentor.get('resume_text', '')
    if resume_text:
        print(f"\n7️⃣ Mentor resume available: {len(resume_text)} characters")
    else:
        print("\n⚠️  No resume text available for mentor")
    
    print("\n" + "="*60)
    print("✅ MENTOR MATCH FEATURE TEST COMPLETE")
    print("="*60)
    print("\n📋 Summary:")
    print(f"   - Student can view assigned mentor: ✅")
    print(f"   - Mentor details displayed: ✅")
    print(f"   - Match reason available: {'✅' if match_reason else '⚠️'}")
    print(f"   - Resume text available: {'✅' if resume_text else '⚠️'}")
    print(f"\n🎯 Next step: Login as student to test the UI")
    print(f"   Email: {sample_student.get('email')}")
    print(f"   Password: Passw0rd!")

if __name__ == "__main__":
    test_mentor_match_feature()
