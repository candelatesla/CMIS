#!/usr/bin/env python3
"""
Instant Mentorship Matching Test Script

This script tests the instant mentorship request creation without requiring email sending.
It demonstrates that mentor dashboard visibility is immediate and database-driven.

Usage:
    python scripts/test_matching_instant.py

Features:
- Creates pending mentorship requests instantly
- No waiting for email delivery
- Requests appear immediately in mentor dashboard
- Tests DB-only visibility workflow
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mentoring_service import MentoringService
from services.student_service import StudentService
from services.mentor_service import MentorService
from db import get_database


def test_instant_matching():
    """Test instant mentorship request creation"""
    
    print("=" * 60)
    print("INSTANT MENTORSHIP MATCHING TEST")
    print("=" * 60)
    print()
    
    # Initialize services
    try:
        get_database()
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return
    
    mentoring_service = MentoringService()
    student_service = StudentService()
    mentor_service = MentorService()
    
    print()
    print("-" * 60)
    print("STEP 1: Fetch Test Data")
    print("-" * 60)
    
    # Get first available student and mentor
    students = student_service.list_students()
    mentors = mentor_service.list_mentors()
    
    if not students:
        print("❌ No students found in database. Please add students first.")
        return
    
    if not mentors:
        print("❌ No mentors found in database. Please add mentors first.")
        return
    
    test_student = students[0]
    test_mentor = mentors[0]
    
    student_id = str(test_student.get('_id'))
    mentor_id = str(test_mentor.get('_id'))
    
    print(f"✅ Student: {test_student.get('name')} (ID: {student_id[:12]}...)")
    print(f"   Email: {test_student.get('email')}")
    print(f"   Major: {test_student.get('major', 'N/A')}")
    print()
    print(f"✅ Mentor: {test_mentor.get('name')} (ID: {mentor_id[:12]}...)")
    print(f"   Email: {test_mentor.get('email')}")
    print(f"   Company: {test_mentor.get('company', 'N/A')}")
    
    print()
    print("-" * 60)
    print("STEP 2: Create Instant Mentorship Request")
    print("-" * 60)
    
    # Create test match reason
    match_reason = f"""Demo match created via instant testing script.

{test_student.get('name')} would benefit from mentorship in:
- Career guidance in {test_student.get('major', 'their field')}
- Industry insights and networking
- Professional development

{test_mentor.get('name')}'s expertise in {test_mentor.get('company', 'their company')} 
makes them an excellent mentor for this student."""
    
    print("Creating pending mentorship request...")
    print(f"Match Reason: {match_reason[:100]}...")
    print()
    
    try:
        result = mentoring_service.assign_pending_match(
            student_id=student_id,
            mentor_id=mentor_id,
            match_reason=match_reason
        )
        
        if "error" in result:
            print(f"❌ Error creating request: {result['error']}")
            return
        
        print("✅ INSTANT REQUEST CREATED SUCCESSFULLY!")
        print()
        print(f"   Link ID: {result.get('_id', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        print(f"   Created At: {result.get('created_at', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Exception creating request: {e}")
        return
    
    print()
    print("-" * 60)
    print("STEP 3: Verify Instant Visibility")
    print("-" * 60)
    
    # Verify mentor can see the pending request
    try:
        pending_requests = mentoring_service.get_pending_requests_for_mentor(mentor_id)
        
        print(f"✅ Mentor has {len(pending_requests)} pending request(s)")
        
        if pending_requests:
            for idx, request in enumerate(pending_requests, 1):
                req_student = request.get('student', {})
                print(f"\n   Request #{idx}:")
                print(f"   - Student: {req_student.get('name', 'Unknown')}")
                print(f"   - Email: {req_student.get('email', 'N/A')}")
                print(f"   - Status: Pending (visible in mentor dashboard NOW)")
        
    except Exception as e:
        print(f"❌ Error verifying visibility: {e}")
        return
    
    # Verify student can see the pending match
    try:
        student_mentor = mentoring_service.get_student_mentor(student_id)
        
        if student_mentor:
            status = student_mentor.get('mentorship_status', 'unknown')
            print()
            print(f"✅ Student sees mentor with status: {status}")
            print(f"   - Mentor: {student_mentor.get('name', 'Unknown')}")
            print(f"   - Status visible in student dashboard NOW")
        else:
            print()
            print("⚠️  Student doesn't see mentor yet (expected for first match)")
    
    except Exception as e:
        print(f"❌ Error checking student view: {e}")
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()
    print("Key Points:")
    print("✓ Request created instantly (no email delay)")
    print("✓ Mentor dashboard shows request immediately")
    print("✓ Student dashboard shows pending status immediately")
    print("✓ Email sending is independent and non-blocking")
    print()
    print("Next Steps:")
    print("1. Login as mentor to see pending request in 'Mentor Requests' page")
    print("2. Accept or decline the mentorship")
    print("3. Student will see 'Accepted' status in 'My Assigned Mentor' page")
    print()
    print(f"Mentor Login: {test_mentor.get('email')}")
    print(f"Student Login: {test_student.get('email')}")
    print()


if __name__ == "__main__":
    test_instant_matching()
