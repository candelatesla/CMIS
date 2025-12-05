"""
Bootstrap script to create auth_users entries for existing students and mentors.
This allows existing database users to log in with default password.

Default password for all users: Passw0rd!

Run this script once to populate auth_users collection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService
from services.student_service import StudentService
from services.mentor_service import MentorService


def bootstrap_students():
    """Create auth_users entries for all existing students"""
    print("🎓 Bootstrapping student accounts...")
    
    auth_service = AuthService()
    student_service = StudentService()
    
    # Get all students
    students = student_service.get_all_students()
    
    created = 0
    skipped = 0
    
    for student in students:
        email = student.get("email")
        student_id = student.get("student_id")
        
        if not email or not student_id:
            print(f"  ⚠️  Skipping student (missing email or ID): {student.get('name', 'Unknown')}")
            skipped += 1
            continue
        
        # Check if auth_user already exists
        existing = auth_service.get_user(email, "student")
        if existing:
            print(f"  ⏭️  Student already has account: {email}")
            skipped += 1
            continue
        
        # Create auth_user with default password
        result = auth_service.create_user(
            email=email,
            password="Passw0rd!",
            role="student",
            linked_student_id=student_id
        )
        
        if "error" in result:
            print(f"  ❌ Error creating account for {email}: {result['error']}")
        else:
            print(f"  ✅ Created account for: {email}")
            created += 1
    
    print(f"\n📊 Student accounts: {created} created, {skipped} skipped")
    return created, skipped


def bootstrap_mentors():
    """Create auth_users entries for all existing mentors"""
    print("\n🧑‍🏫 Bootstrapping mentor accounts...")
    
    auth_service = AuthService()
    mentor_service = MentorService()
    
    # Get all mentors
    mentors = mentor_service.get_all_mentors()
    
    created = 0
    skipped = 0
    
    for mentor in mentors:
        email = mentor.get("email")
        mentor_id = mentor.get("mentor_id")
        
        if not email or not mentor_id:
            print(f"  ⚠️  Skipping mentor (missing email or ID): {mentor.get('name', 'Unknown')}")
            skipped += 1
            continue
        
        # Check if auth_user already exists
        existing = auth_service.get_user(email, "mentor")
        if existing:
            print(f"  ⏭️  Mentor already has account: {email}")
            skipped += 1
            continue
        
        # Create auth_user with default password
        result = auth_service.create_user(
            email=email,
            password="Passw0rd!",
            role="mentor",
            linked_mentor_id=mentor_id
        )
        
        if "error" in result:
            print(f"  ❌ Error creating account for {email}: {result['error']}")
        else:
            print(f"  ✅ Created account for: {email}")
            created += 1
    
    print(f"\n📊 Mentor accounts: {created} created, {skipped} skipped")
    return created, skipped


def main():
    """Main bootstrap function"""
    print("=" * 60)
    print("🚀 CMIS Auth Users Bootstrap Script")
    print("=" * 60)
    print("\nThis script will create auth_users entries for all existing")
    print("students and mentors with the default password: Passw0rd!")
    print("\n⚠️  Users should change their password after first login.")
    print("\n" + "=" * 60)
    
    input("\nPress Enter to continue (Ctrl+C to cancel)...")
    
    # Bootstrap students
    student_created, student_skipped = bootstrap_students()
    
    # Bootstrap mentors
    mentor_created, mentor_skipped = bootstrap_mentors()
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ Bootstrap Complete!")
    print("=" * 60)
    print(f"Students: {student_created} created, {student_skipped} skipped")
    print(f"Mentors: {mentor_created} created, {mentor_skipped} skipped")
    print(f"Total: {student_created + mentor_created} new accounts created")
    print("\n💡 Default password for all accounts: Passw0rd!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Bootstrap cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        sys.exit(1)
