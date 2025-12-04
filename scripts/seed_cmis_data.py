"""
CMIS Case Competition Platform - Database Seed Script
Populates MongoDB with mentors, events, competitions, and judges
"""
import sys
import os
import random
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mentor_service import MentorService
from services.event_service import EventService
from services.case_comp_service import CaseCompService
from utils.pdf_utils import get_random_mentor_resume


# ============================================================================
# MENTOR DATA CONFIGURATION
# ============================================================================

MENTOR_NAMES = [
    "Blaine Bryant",
    "Jeff Richardson",
    "Nikhil Gupta",
    "Mahidhar Panyam",
    "Suryakant Kaushik",
    "John Billings",
    "Divyesh Batra"
]

COMPANIES = [
    "Microsoft",
    "Amazon Web Services",
    "Google Cloud",
    "IBM Consulting",
    "Deloitte Digital",
    "Accenture",
    "Oracle",
    "Salesforce",
    "SAP",
    "Cisco Systems",
    "VMware",
    "Red Hat"
]

JOB_TITLES = [
    "Cloud Solutions Architect",
    "Principal Security Engineer",
    "Senior Data Scientist",
    "Director of Engineering",
    "Lead Cloud Architect",
    "VP of Technology",
    "Chief Information Security Officer",
    "Principal Engineer",
    "Director of Data Engineering",
    "Enterprise Architect"
]

INDUSTRIES = [
    "Cloud Computing",
    "Cybersecurity",
    "IT Consulting",
    "Enterprise Software",
    "Data Analytics",
    "Artificial Intelligence",
    "DevOps & Infrastructure"
]

EXPERTISE_POOL = [
    "Cloud Architecture",
    "AWS Solutions",
    "Azure Infrastructure",
    "Google Cloud Platform",
    "Kubernetes & Container Orchestration",
    "Microservices Architecture",
    "Cybersecurity",
    "Network Security",
    "Identity & Access Management",
    "Data Science",
    "Machine Learning",
    "Big Data Analytics",
    "DevOps",
    "CI/CD Pipelines",
    "Infrastructure as Code",
    "Enterprise Systems",
    "System Design",
    "Technical Leadership",
    "Agile Methodologies",
    "Team Management"
]

INTERESTS_POOL = [
    "Mentoring",
    "Public Speaking",
    "Open Source",
    "Innovation",
    "AI/ML Research",
    "Cloud Technologies",
    "Security Best Practices",
    "Technical Writing",
    "Community Building",
    "Entrepreneurship"
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_email(name):
    """Generate email from name"""
    parts = name.lower().split()
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}@techcorp.com"
    return f"{parts[0]}@techcorp.com"


def generate_mentor_id(name):
    """Generate mentor_id from name"""
    parts = name.upper().split()
    if len(parts) >= 2:
        return f"MEN{parts[1][:3]}{parts[0][:2]}"
    return f"MEN{parts[0][:5]}"


def generate_mentor_data(name):
    """Generate complete mentor data for a given name"""
    return {
        "name": name,
        "email": generate_email(name),
        "mentor_id": generate_mentor_id(name),
        "company": random.choice(COMPANIES),
        "job_title": random.choice(JOB_TITLES),
        "industry": random.choice(INDUSTRIES),
        "years_experience": random.randint(10, 25),
        "expertise_areas": random.sample(EXPERTISE_POOL, random.randint(4, 6)),
        "interests": random.sample(INTERESTS_POOL, random.randint(3, 5)),
        "max_mentees": random.randint(2, 6),
        "current_mentees": 0,
        "linkedin_url": f"https://linkedin.com/in/{name.lower().replace(' ', '')}",
        "resume_text": get_random_mentor_resume()
    }


def mentor_exists(service, name, email):
    """Check if mentor already exists by name or email"""
    all_mentors = service.list_mentors()
    for mentor in all_mentors:
        if mentor.get('name') == name or mentor.get('email') == email:
            return True
    return False


def event_exists(service, event_id):
    """Check if event already exists by event_id"""
    event = service.get_event_by_id(event_id)
    return event and 'error' not in event


def competition_exists(service, competition_id):
    """Check if competition already exists by competition_id"""
    comp = service.get_case_competition_by_id(competition_id)
    return comp and 'error' not in comp


# ============================================================================
# SEEDING FUNCTIONS
# ============================================================================

def seed_mentors():
    """Seed 7 mentors into the database"""
    print("\n" + "="*60)
    print("SEEDING MENTORS")
    print("="*60)
    
    service = MentorService()
    created_count = 0
    skipped_count = 0
    
    for name in MENTOR_NAMES:
        mentor_data = generate_mentor_data(name)
        
        # Check if mentor exists
        if mentor_exists(service, name, mentor_data['email']):
            print(f"[SKIP] Mentor '{name}' already exists")
            skipped_count += 1
            continue
        
        # Create mentor
        result = service.create_mentor(mentor_data)
        
        if "error" in result:
            print(f"[ERROR] Failed to create mentor '{name}': {result['error']}")
        else:
            print(f"[OK] Mentor '{name}' created - {mentor_data['job_title']} at {mentor_data['company']}")
            created_count += 1
    
    print(f"\n✅ Mentors: {created_count} created, {skipped_count} skipped")
    return created_count, skipped_count


def seed_event():
    """Seed the CMIS Fall Case Competition 2025 event"""
    print("\n" + "="*60)
    print("SEEDING EVENT")
    print("="*60)
    
    service = EventService()
    event_id = "cmis_fall_case_comp_2025"
    
    # Check if event exists
    if event_exists(service, event_id):
        print(f"[SKIP] Event '{event_id}' already exists")
        return 0, 1
    
    # Create event with exact specifications
    # CST is UTC-6, so 9:00 AM CST = 3:00 PM UTC
    event_data = {
        "event_id": event_id,
        "name": "CMIS Fall Case Competition 2025",
        "description": "Annual CMIS case competition featuring industry judges and student teams. Focus on AI-driven business solutions.",
        "event_type": "Case Competition",
        "location": "Mays Business School, Texas A&M University",
        "start_datetime": datetime(2025, 12, 5, 15, 0, 0, tzinfo=timezone.utc),  # 9:00 AM CST
        "end_datetime": datetime(2025, 12, 5, 23, 0, 0, tzinfo=timezone.utc),    # 5:00 PM CST
        "capacity": 200,
        "registration_required": True,
        "sponsor_tier": "ExaByte",
        "registered_students": []
    }
    
    result = service.create_event(event_data)
    
    if "error" in result:
        print(f"[ERROR] Failed to create event: {result['error']}")
        return 0, 0
    else:
        print(f"[OK] Event '{event_data['name']}' created")
        print(f"     Location: {event_data['location']}")
        print(f"     Date: December 5, 2025")
        print(f"     Capacity: {event_data['capacity']}")
        return 1, 0


def seed_competition_and_judges():
    """Seed the case competition and add all 7 judges"""
    print("\n" + "="*60)
    print("SEEDING CASE COMPETITION & JUDGES")
    print("="*60)
    
    service = CaseCompService()
    competition_id = "cmis_comp_2025"
    
    # Check if competition exists
    comp_exists = competition_exists(service, competition_id)
    
    if not comp_exists:
        # Create competition
        comp_data = {
            "competition_id": competition_id,
            "name": "CMIS AI Strategy Case Competition",
            "description": "AI business strategy presentation competition using the CMIS engagement platform.",
            "event_id": "cmis_fall_case_comp_2025",
            "team_size_min": 2,
            "team_size_max": 4,
            "judges": [],
            "teams": [],
            "prizes": "1st: $5000, 2nd: $3000, 3rd: $1500"
        }
        
        result = service.create_case_competition(comp_data)
        
        if "error" in result:
            print(f"[ERROR] Failed to create competition: {result['error']}")
            return 0, 0
        else:
            print(f"[OK] Competition '{comp_data['name']}' created")
    else:
        print(f"[SKIP] Competition '{competition_id}' already exists")
    
    # Now add judges (idempotent)
    comp = service.get_case_competition_by_id(competition_id)
    if not comp or 'error' in comp:
        print("[ERROR] Could not retrieve competition to add judges")
        return 0 if not comp_exists else 1, 1 if comp_exists else 0
    
    current_judges = comp.get('judges', [])
    judges_to_add = []
    
    for name in MENTOR_NAMES:
        if name not in current_judges:
            judges_to_add.append(name)
    
    if judges_to_add:
        # Update competition with new judges
        updated_judges = current_judges + judges_to_add
        result = service.update_case_competition(comp['_id'], {"judges": updated_judges})
        
        if "error" in result:
            print(f"[ERROR] Failed to update judges: {result['error']}")
        else:
            print(f"[OK] Added {len(judges_to_add)} judges to competition")
            for judge in judges_to_add:
                print(f"     + {judge}")
    else:
        print(f"[SKIP] All 7 judges already added")
    
    print(f"\n✅ Competition: 1 updated with {len(current_judges) + len(judges_to_add)} judges")
    return 1 if not comp_exists else 0, 1 if comp_exists else 0


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("CMIS CASE COMPETITION PLATFORM - DATABASE SEEDING")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Seed mentors
        mentors_created, mentors_skipped = seed_mentors()
        
        # Seed event
        events_created, events_skipped = seed_event()
        
        # Seed competition and judges
        comp_created, comp_skipped = seed_competition_and_judges()
        
        # Final summary
        print("\n" + "="*60)
        print("SEEDING COMPLETE")
        print("="*60)
        print(f"Mentors:      {mentors_created} created, {mentors_skipped} skipped")
        print(f"Events:       {events_created} created, {events_skipped} skipped")
        print(f"Competitions: {comp_created} created, {comp_skipped} skipped")
        print(f"Judges:       7 names added to competition")
        print("\n✅ Database seeding successful!")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 View results in Streamlit: http://localhost:8506")
        
    except Exception as e:
        print(f"\n❌ ERROR during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
