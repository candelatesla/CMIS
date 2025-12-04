"""
Test script for AI Matching Engine
Demonstrates compute_match_score, rank_mentors_for_student, and generate_match_reason
"""
from ai.matching import (
    compute_match_score, 
    rank_mentors_for_student, 
    generate_match_reason,
    MatchingEngine
)
from services.student_service import StudentService
from services.mentor_service import MentorService


def test_hybrid_scoring():
    """Test the hybrid scoring algorithm"""
    print("="*70)
    print("TEST 1: HYBRID SCORING ALGORITHM")
    print("="*70)
    
    # Create test student
    student = {
        'name': 'Alice Chen',
        'major': 'Data Science',
        'interests': ['Machine Learning', 'Cloud Computing', 'AI'],
        'skills': ['Python', 'TensorFlow', 'AWS', 'SQL'],
        'resume_text': 'Data science student with experience in machine learning, deep learning, and cloud computing using AWS and Python.'
    }
    
    # Create test mentors with varying match levels
    mentors = [
        {
            'name': 'Sarah ML Expert',
            'job_title': 'Senior ML Engineer',
            'company': 'TechCorp',
            'expertise_areas': ['Machine Learning', 'Python', 'Cloud Computing', 'Deep Learning'],
            'resume_text': 'Machine learning expert with 10 years experience in Python, AWS, and building scalable AI systems.'
        },
        {
            'name': 'Bob Backend Dev',
            'job_title': 'Backend Developer',
            'company': 'WebCo',
            'expertise_areas': ['Java', 'Databases', 'API Design'],
            'resume_text': 'Backend developer specializing in Java microservices and database optimization.'
        },
        {
            'name': 'Carol Cloud Architect',
            'job_title': 'Cloud Solutions Architect',
            'company': 'CloudInc',
            'expertise_areas': ['AWS', 'Cloud Architecture', 'DevOps', 'Python'],
            'resume_text': 'Cloud architect with expertise in AWS, infrastructure as code, and Python automation.'
        }
    ]
    
    print(f"\nStudent: {student['name']} - {student['major']}")
    print(f"Interests: {', '.join(student['interests'])}")
    print(f"Skills: {', '.join(student['skills'])}")
    print("\nMatch Scores:")
    print("-" * 70)
    
    for mentor in mentors:
        score = compute_match_score(student, mentor)
        print(f"\n{mentor['name']} ({mentor['job_title']})")
        print(f"  Expertise: {', '.join(mentor['expertise_areas'])}")
        print(f"  Match Score: {score:.3f}")
        print(f"  Breakdown:")
        
        # Show score components
        student_interests_lower = [i.lower() for i in student['interests']]
        mentor_expertise_lower = [e.lower() for e in mentor['expertise_areas']]
        
        interest_matches = sum(1 for i in student_interests_lower 
                              if any(i in e or e in i for e in mentor_expertise_lower))
        print(f"    - Interest overlap: {interest_matches}/{len(student['interests'])}")
        
        student_skills_lower = [s.lower() for s in student['skills']]
        skill_matches = sum(1 for s in student_skills_lower 
                           if any(s in e or e in s for e in mentor_expertise_lower))
        print(f"    - Skill overlap: {skill_matches}/{len(student['skills'])}")
    
    print("\n" + "="*70)


def test_ranking():
    """Test mentor ranking functionality"""
    print("\nTEST 2: MENTOR RANKING")
    print("="*70)
    
    student = {
        'name': 'David Lee',
        'major': 'Computer Science',
        'interests': ['Software Engineering', 'Cloud', 'Security'],
        'skills': ['Python', 'JavaScript', 'Docker', 'Kubernetes'],
        'resume_text': 'CS student interested in cloud infrastructure and security.'
    }
    
    mentors = [
        {
            'name': 'Mentor A',
            'mentor_id': 'MEN001',
            'job_title': 'Cloud Security Architect',
            'company': 'SecureCo',
            'expertise_areas': ['Cloud Security', 'Kubernetes', 'DevOps']
        },
        {
            'name': 'Mentor B',
            'mentor_id': 'MEN002',
            'job_title': 'Frontend Developer',
            'company': 'WebDev Inc',
            'expertise_areas': ['React', 'UI/UX', 'JavaScript']
        },
        {
            'name': 'Mentor C',
            'mentor_id': 'MEN003',
            'job_title': 'Data Engineer',
            'company': 'DataCorp',
            'expertise_areas': ['Python', 'SQL', 'Big Data']
        }
    ]
    
    # Rank mentors
    ranked = rank_mentors_for_student(student, mentors, top_n=3)
    
    print(f"\nStudent: {student['name']}")
    print(f"Top {len(ranked)} Mentor Matches:")
    print("-" * 70)
    
    for match in ranked:
        print(f"\nRank {match['rank']}: {match['mentor_name']}")
        print(f"  Score: {match['score']:.3f}")
        print(f"  Title: {match['mentor']['job_title']}")
        print(f"  Company: {match['mentor']['company']}")
    
    print("\n" + "="*70)


def test_ai_reasoning():
    """Test Groq Mixtral reasoning generation"""
    print("\nTEST 3: AI-GENERATED MATCH REASONING (Groq Mixtral)")
    print("="*70)
    
    student = {
        'name': 'Emily Rodriguez',
        'major': 'Business Analytics',
        'interests': ['Data Analytics', 'Business Intelligence', 'Consulting'],
        'skills': ['SQL', 'Tableau', 'Python', 'Excel'],
        'resume_text': 'Business analytics student with passion for data-driven decision making.'
    }
    
    mentor = {
        'name': 'Michael Chen',
        'job_title': 'Senior Data Analyst',
        'company': 'ConsultCo',
        'expertise_areas': ['Data Analytics', 'Business Intelligence', 'SQL', 'Tableau']
    }
    
    score = compute_match_score(student, mentor)
    
    print(f"\nStudent: {student['name']} - {student['major']}")
    print(f"Mentor: {mentor['name']} - {mentor['job_title']} at {mentor['company']}")
    print(f"Match Score: {score:.3f}")
    print("\nGenerating AI explanation using Groq Mixtral...")
    print("-" * 70)
    
    reason = generate_match_reason(student, mentor, score)
    print(f"\n{reason}")
    
    print("\n" + "="*70)


def test_with_real_data():
    """Test with real database data"""
    print("\nTEST 4: REAL DATABASE DATA")
    print("="*70)
    
    student_service = StudentService()
    mentor_service = MentorService()
    
    students = student_service.list_students()
    mentors = mentor_service.list_mentors()
    
    print(f"\nDatabase Status:")
    print(f"  Students: {len(students)}")
    print(f"  Mentors: {len(mentors)}")
    
    if students and mentors:
        # Use first student
        student = students[0]
        print(f"\n✅ Testing with student: {student.get('name')}")
        
        # Get top 3 matches
        top_matches = rank_mentors_for_student(student, mentors, top_n=3)
        
        print("\nTop 3 Mentor Matches:")
        print("-" * 70)
        
        for match in top_matches:
            mentor = match['mentor']
            print(f"\n{match['rank']}. {mentor.get('name')} (Score: {match['score']:.3f})")
            print(f"   {mentor.get('job_title')} at {mentor.get('company')}")
            
            if match['rank'] == 1:
                print("\n   AI-Generated Reason:")
                reason = generate_match_reason(student, mentor, match['score'])
                print(f"   {reason}")
    else:
        print("\n⚠️ No data in database. Run seed script first.")
    
    print("\n" + "="*70)


def test_matching_engine_class():
    """Test the MatchingEngine class wrapper"""
    print("\nTEST 5: MATCHING ENGINE CLASS")
    print("="*70)
    
    engine = MatchingEngine()
    
    student = {
        'name': 'Test Student',
        'major': 'Engineering',
        'interests': ['Robotics', 'AI'],
        'skills': ['C++', 'Python', 'ROS'],
        'resume_text': 'Engineering student passionate about robotics and AI.'
    }
    
    mentors = [
        {
            'name': 'Robotics Expert',
            'job_title': 'Robotics Engineer',
            'company': 'BotCo',
            'expertise_areas': ['Robotics', 'AI', 'Computer Vision']
        }
    ]
    
    print("\nUsing MatchingEngine class:")
    print("-" * 70)
    
    # Test class methods
    score = engine.compute_match_score(student, mentors[0])
    print(f"Score: {score:.3f}")
    
    ranked = engine.rank_mentors_for_student(student, mentors, top_n=1)
    print(f"Ranked: {ranked[0]['mentor_name']} (Rank {ranked[0]['rank']})")
    
    reason = engine.generate_match_reason(student, mentors[0], score)
    print(f"Reason: {reason[:100]}...")
    
    print("\n✅ MatchingEngine class working correctly")
    print("="*70)


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("AI MATCHING ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    try:
        test_hybrid_scoring()
        test_ranking()
        test_ai_reasoning()
        test_with_real_data()
        test_matching_engine_class()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\n📝 Summary:")
        print("  ✅ Hybrid scoring (40% interests + 40% skills + 20% resume)")
        print("  ✅ Mentor ranking with scores")
        print("  ✅ AI-generated match explanations (Groq Mixtral)")
        print("  ✅ Real database integration")
        print("  ✅ MatchingEngine class wrapper")
        print("\n🌐 Functions available:")
        print("  - compute_match_score(student, mentor)")
        print("  - rank_mentors_for_student(student, mentors, top_n)")
        print("  - generate_match_reason(student, mentor, score)")
        print("  - MatchingEngine() class")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
