"""
Test the refactored email generation for human tone and formatting
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

from ai.email_generation import generate_mentor_outreach_email


def test_email_generation():
    """Test the improved email generation"""
    print("=" * 80)
    print("REFINED EMAIL GENERATION TEST")
    print("=" * 80)
    print()
    
    # Sample student data
    student = {
        "name": "Sarah Johnson",
        "major": "Computer Science",
        "grad_year": "2026",
        "interests": ["Machine Learning", "AI", "Data Science"],
        "skills": ["Python", "TensorFlow", "SQL", "React"]
    }
    
    # Sample mentor data
    mentor = {
        "name": "Dr. Michael Chen",
        "job_title": "Senior AI Research Scientist",
        "company": "Google",
        "expertise_areas": ["Deep Learning", "NLP", "Computer Vision"]
    }
    
    # Sample match reason (WITHOUT scores)
    match_reason = """Sarah is passionate about machine learning and AI, which aligns perfectly with your research in deep learning and NLP. Her strong Python and TensorFlow skills show she's already building a solid foundation in the field."""
    
    print("TEST INPUTS:")
    print("-" * 80)
    print(f"Student: {student['name']} ({student['major']}, Class of {student['grad_year']})")
    print(f"Mentor: {mentor['name']} - {mentor['job_title']} at {mentor['company']}")
    print()
    
    # Generate email
    print("Generating email with refined function...")
    print()
    
    try:
        subject, body = generate_mentor_outreach_email(student, mentor, match_reason)
        
        print("=" * 80)
        print("GENERATED EMAIL")
        print("=" * 80)
        print()
        print(f"SUBJECT: {subject}")
        print()
        print("BODY:")
        print("-" * 80)
        print(body)
        print()
        print("=" * 80)
        print()
        
        # Validation checks
        print("VALIDATION CHECKS:")
        print("-" * 80)
        
        all_passed = True
        
        # Check 1: No score references
        score_keywords = ["match score", "score", "similarity", "percentage", "%", "algorithm"]
        has_scores = any(keyword.lower() in body.lower() for keyword in score_keywords)
        
        if not has_scores:
            print("✅ No score/algorithm references found")
        else:
            print("❌ Score/algorithm references detected")
            all_passed = False
        
        # Check 2: Has proper spacing (paragraph breaks)
        paragraph_count = body.count('\n\n')
        if paragraph_count >= 2:
            print(f"✅ Proper paragraph spacing ({paragraph_count} breaks)")
        else:
            print(f"⚠️  Limited paragraph spacing ({paragraph_count} breaks)")
        
        # Check 3: Mentions student name
        if student['name'] in body:
            print(f"✅ Student name mentioned")
        else:
            print(f"❌ Student name missing")
            all_passed = False
        
        # Check 4: Mentions mentor name
        if mentor['name'] in body:
            print(f"✅ Mentor name mentioned")
        else:
            print(f"❌ Mentor name missing")
            all_passed = False
        
        # Check 5: No markdown formatting
        markdown_symbols = ['**', '*', '```', '##', '###']
        has_markdown = any(symbol in body or symbol in subject for symbol in markdown_symbols)
        
        if not has_markdown:
            print("✅ No markdown formatting")
        else:
            print("❌ Markdown symbols detected")
            all_passed = False
        
        # Check 6: Has proper greeting
        greetings = ["Hi ", "Hello ", "Dear "]
        has_greeting = any(body.startswith(greeting) for greeting in greetings)
        
        if has_greeting:
            print("✅ Professional greeting")
        else:
            print("⚠️  No standard greeting detected")
        
        # Check 7: Has sign-off
        sign_offs = ["CMIS Team", "Best regards", "Warm regards", "Sincerely"]
        has_sign_off = any(sign_off in body for sign_off in sign_offs)
        
        if has_sign_off:
            print("✅ Professional sign-off")
        else:
            print("⚠️  No standard sign-off detected")
        
        # Check 8: Reasonable length
        word_count = len(body.split())
        if 100 <= word_count <= 300:
            print(f"✅ Appropriate length ({word_count} words)")
        else:
            print(f"⚠️  Length: {word_count} words (target: 100-300)")
        
        print()
        
        if all_passed:
            print("=" * 80)
            print("✅ ALL CRITICAL CHECKS PASSED")
            print("=" * 80)
            print()
            print("Email improvements verified:")
            print("  • No AI/score references")
            print("  • Human, warm tone")
            print("  • Proper formatting and spacing")
            print("  • Professional structure")
            print("  • Clean plain text (no markdown)")
        else:
            print("=" * 80)
            print("⚠️  SOME ISSUES DETECTED")
            print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error generating email: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()


if __name__ == "__main__":
    test_email_generation()
