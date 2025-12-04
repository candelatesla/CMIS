"""
Test script for the AI matching engine.

This script:
1. Loads all mentors from the database (the 7 seeded judges)
2. Loads all students from the database
3. For each student, runs the matching engine to find top 3 mentor matches
4. Prints formatted results with scores and AI-generated explanations
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mentor_service import MentorService
from services.student_service import StudentService
from ai.matching import MatchingEngine


def print_header():
    """Print a nice header for the test output."""
    print()
    print("=" * 80)
    print("CMIS AI MATCHING ENGINE - TEST RESULTS")
    print("=" * 80)
    print()


def print_student_header(student_name, student_major, student_year):
    """Print header for each student's matches."""
    print()
    print("─" * 80)
    print(f"🎓 STUDENT: {student_name} | {student_major} | Class of {student_year}")
    print("─" * 80)


def print_match(rank, mentor_name, score, reason):
    """Print a single match result."""
    # Format score as percentage
    score_pct = f"{score * 100:.1f}%"
    
    print(f"\n{rank}. 👔 Mentor: {mentor_name}")
    print(f"   📊 Match Score: {score_pct}")
    print(f"   💡 Reason: {reason}")


def test_matching_engine():
    """Run the matching engine test."""
    print_header()
    
    # Initialize services
    mentor_service = MentorService()
    student_service = StudentService()
    
    # Load all mentors
    print("Loading mentors from database...")
    mentors = mentor_service.list_mentors()
    
    if not mentors:
        print("❌ ERROR: No mentors found in database!")
        print("   Please run: python scripts/seed_cmis_data.py")
        return
    
    print(f"✅ Loaded {len(mentors)} mentors")
    
    # Load all students
    print("Loading students from database...")
    students = student_service.list_students()
    
    if not students:
        print("❌ ERROR: No students found in database!")
        print("   Please run: python scripts/seed_students.py")
        return
    
    print(f"✅ Loaded {len(students)} students")
    print()
    
    # Initialize matching engine
    print("Initializing AI matching engine...")
    engine = MatchingEngine()
    print("✅ Matching engine ready")
    
    # Process each student
    success_count = 0
    error_count = 0
    
    for student in students:
        try:
            # Skip students with missing required fields
            if not student.get("interests") or not student.get("skills"):
                print(f"⏭️  SKIPPED: {student.get('name', 'Unknown')} - Missing interests or skills")
                continue
            
            # Print student header
            print_student_header(
                student.get("name", "Unknown"),
                student.get("major", "Unknown"),
                student.get("grad_year", "Unknown")
            )
            
            # Find top 3 matches with AI-generated reasons
            matches = engine.find_best_matches(
                student=student,
                available_mentors=mentors,
                top_k=3,
                include_reasons=True
            )
            
            if not matches:
                print("   ⚠️  No matches found for this student")
                continue
            
            # Print each match
            for match in matches:
                print_match(
                    rank=match["rank"],
                    mentor_name=match["mentor_name"],
                    score=match["score"],
                    reason=match.get("reason", "AI explanation not available")
                )
            
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ ERROR processing student: {str(e)}")
            error_count += 1
    
    # Print summary
    print()
    print("=" * 80)
    print("MATCHING TEST COMPLETE")
    print(f"  ✅ Successfully matched: {success_count} students")
    if error_count > 0:
        print(f"  ❌ Errors encountered: {error_count} students")
    print("=" * 80)
    print()


if __name__ == "__main__":
    try:
        test_matching_engine()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
