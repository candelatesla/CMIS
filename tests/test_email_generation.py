"""
Quick test for generate_mentor_outreach_email function
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.email_generation import generate_mentor_outreach_email

# Test with sample data
student = {
    "name": "Sarah Chen",
    "major": "Computer Science",
    "grad_year": 2026,
    "interests": ["Distributed Systems", "Cloud Architecture", "Machine Learning"],
    "skills": ["Python", "Java", "Docker", "Kubernetes", "AWS", "React"]
}

mentor = {
    "name": "Blaine Bryant",
    "job_title": "Senior Engineering Manager",
    "company": "Microsoft",
    "expertise_areas": ["Software Engineering", "Cloud Computing", "Team Leadership"]
}

match_reason = "Sarah's strong technical foundation in cloud technologies and distributed systems aligns perfectly with Blaine's extensive experience at Microsoft. This mentorship could provide valuable insights into enterprise-scale cloud architecture and career growth in big tech."

print("=" * 80)
print("TESTING: generate_mentor_outreach_email()")
print("=" * 80)
print()

try:
    subject, body = generate_mentor_outreach_email(student, mentor, match_reason)
    
    print("✅ Email generated successfully!")
    print()
    print("-" * 80)
    print(f"SUBJECT: {subject}")
    print("-" * 80)
    print()
    print(body)
    print()
    print("-" * 80)
    print()
    print(f"Subject length: {len(subject)} characters")
    print(f"Body length: {len(body)} characters")
    print()
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
