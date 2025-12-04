"""
Seed script to populate the database with 20 realistic student profiles.

This script creates 20 diverse students across different majors:
- MIS (Management Information Systems)
- CSCE (Computer Science)
- CYBR (Cybersecurity)
- ISEN (Industrial and Systems Engineering)
- STAT (Statistics)

The script is idempotent - it will skip students that already exist.
"""

import sys
import os
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.student_service import StudentService
from utils.pdf_utils import get_random_student_resume

def student_exists(student_service, student_id):
    """Check if a student already exists in the database."""
    try:
        student = student_service.get_student_by_id(student_id)
        return student is not None
    except:
        return False


def generate_student_data():
    """Generate data for 20 realistic students."""
    
    # Define student profiles with varied interests and skills across majors
    students = [
        {
            "student_id": "234567890",
            "name": "Alex Martinez",
            "email": "amartinez@tamu.edu",
            "major": "MIS",
            "grad_year": 2025,
            "interests": ["Business Intelligence", "Data Analytics", "Enterprise Systems"],
            "skills": ["SQL", "Python", "Tableau", "Power BI", "SAP", "Salesforce"]
        },
        {
            "student_id": "345678901",
            "name": "Sarah Chen",
            "email": "schen@tamu.edu",
            "major": "CSCE",
            "grad_year": 2026,
            "interests": ["Distributed Systems", "Cloud Architecture", "Machine Learning"],
            "skills": ["Python", "Java", "C++", "Docker", "Kubernetes", "AWS", "React"]
        },
        {
            "student_id": "456789012",
            "name": "Michael Johnson",
            "email": "mjohnson@tamu.edu",
            "major": "CYBR",
            "grad_year": 2025,
            "interests": ["Ethical Hacking", "Network Security", "Malware Analysis"],
            "skills": ["Python", "Kali Linux", "Wireshark", "Nmap", "Splunk", "Penetration Testing"]
        },
        {
            "student_id": "567890123",
            "name": "Emily Rodriguez",
            "email": "erodriguez@tamu.edu",
            "major": "MIS",
            "grad_year": 2026,
            "interests": ["Digital Transformation", "Business Process Optimization", "ERP Systems"],
            "skills": ["Salesforce", "SAP", "Tableau", "Power BI", "Python", "SQL"]
        },
        {
            "student_id": "678901234",
            "name": "David Park",
            "email": "dpark@tamu.edu",
            "major": "ISEN",
            "grad_year": 2025,
            "interests": ["Supply Chain Optimization", "Data Analytics", "Process Improvement"],
            "skills": ["Python", "R", "MATLAB", "SQL", "Arena", "Tableau", "Six Sigma"]
        },
        {
            "student_id": "789012345",
            "name": "Jessica Williams",
            "email": "jwilliams@tamu.edu",
            "major": "CSCE",
            "grad_year": 2027,
            "interests": ["Web Development", "Artificial Intelligence", "Mobile Apps"],
            "skills": ["Python", "JavaScript", "React", "Node.js", "MongoDB", "Git"]
        },
        {
            "student_id": "890123456",
            "name": "Brandon Taylor",
            "email": "btaylor@tamu.edu",
            "major": "CYBR",
            "grad_year": 2026,
            "interests": ["Network Security", "Incident Response", "Penetration Testing"],
            "skills": ["Python", "Bash", "Wireshark", "Nmap", "Linux", "Cloud Security"]
        },
        {
            "student_id": "901234567",
            "name": "Rachel Kim",
            "email": "rkim@tamu.edu",
            "major": "MIS",
            "grad_year": 2025,
            "interests": ["Business Intelligence", "Data Warehousing", "Predictive Analytics"],
            "skills": ["Tableau", "Power BI", "SQL", "Python", "R", "ETL"]
        },
        {
            "student_id": "012345678",
            "name": "Christopher Lee",
            "email": "clee@tamu.edu",
            "major": "CSCE",
            "grad_year": 2025,
            "interests": ["Software Architecture", "Backend Development", "API Design"],
            "skills": ["Java", "Python", "Spring Boot", "Django", "PostgreSQL", "Docker"]
        },
        {
            "student_id": "123456780",
            "name": "Amanda Garcia",
            "email": "agarcia@tamu.edu",
            "major": "STAT",
            "grad_year": 2026,
            "interests": ["Machine Learning", "Data Visualization", "Experimental Design"],
            "skills": ["R", "Python", "SAS", "SQL", "Tableau", "Machine Learning"]
        },
        {
            "student_id": "234567891",
            "name": "Kevin Nguyen",
            "email": "knguyen@tamu.edu",
            "major": "ISEN",
            "grad_year": 2026,
            "interests": ["Operations Research", "Supply Chain Management", "Process Optimization"],
            "skills": ["Python", "SQL", "MATLAB", "Arena", "Tableau", "Six Sigma"]
        },
        {
            "student_id": "345678902",
            "name": "Olivia Thompson",
            "email": "othompson@tamu.edu",
            "major": "MIS",
            "grad_year": 2027,
            "interests": ["Digital Marketing", "User Experience Design", "E-Commerce"],
            "skills": ["Salesforce", "SQL", "Tableau", "HTML", "CSS", "JavaScript"]
        },
        {
            "student_id": "456789013",
            "name": "Daniel Martinez",
            "email": "dmartinez@tamu.edu",
            "major": "CYBR",
            "grad_year": 2025,
            "interests": ["Security Operations", "Threat Intelligence", "Security Automation"],
            "skills": ["Python", "Splunk", "Wireshark", "PowerShell", "AWS Security", "Go"]
        },
        {
            "student_id": "567890124",
            "name": "Sophia Anderson",
            "email": "sanderson@tamu.edu",
            "major": "CSCE",
            "grad_year": 2026,
            "interests": ["Machine Learning", "Computer Vision", "Natural Language Processing"],
            "skills": ["Python", "TensorFlow", "PyTorch", "OpenCV", "Docker", "AWS"]
        },
        {
            "student_id": "678901235",
            "name": "Ryan Hall",
            "email": "rhall@tamu.edu",
            "major": "STAT",
            "grad_year": 2025,
            "interests": ["Data Science", "Predictive Analytics", "Statistical Modeling"],
            "skills": ["R", "Python", "SAS", "SQL", "Tableau", "Machine Learning"]
        },
        {
            "student_id": "789012346",
            "name": "Madison White",
            "email": "mwhite@tamu.edu",
            "major": "MIS",
            "grad_year": 2026,
            "interests": ["Enterprise Systems", "Business Process Management", "Digital Transformation"],
            "skills": ["SAP", "Salesforce", "SQL", "Python", "Power BI", "Power Automate"]
        },
        {
            "student_id": "890123457",
            "name": "Ethan Brown",
            "email": "ebrown@tamu.edu",
            "major": "CSCE",
            "grad_year": 2025,
            "interests": ["Computer Networks", "Network Security", "Systems Programming"],
            "skills": ["C", "C++", "Python", "Go", "Wireshark", "Linux", "Networking"]
        },
        {
            "student_id": "901234568",
            "name": "Isabella Davis",
            "email": "idavis@tamu.edu",
            "major": "ISEN",
            "grad_year": 2025,
            "interests": ["Process Excellence", "Quality Management", "Healthcare Operations"],
            "skills": ["Python", "R", "SQL", "Minitab", "Arena", "Six Sigma", "Lean"]
        },
        {
            "student_id": "012345679",
            "name": "Nathan Wilson",
            "email": "nwilson@tamu.edu",
            "major": "CYBR",
            "grad_year": 2027,
            "interests": ["Ethical Hacking", "Application Security", "Cryptography"],
            "skills": ["Python", "Kali Linux", "Wireshark", "Nmap", "Linux", "Bash"]
        },
        {
            "student_id": "123456781",
            "name": "Grace Martinez",
            "email": "gmartinez@tamu.edu",
            "major": "STAT",
            "grad_year": 2027,
            "interests": ["Data Science", "Statistical Learning", "Data Visualization"],
            "skills": ["R", "Python", "SQL", "MATLAB", "Git", "LaTeX"]
        }
    ]
    
    return students


def seed_students():
    """Seed the database with 20 student profiles."""
    print("=" * 70)
    print("CMIS STUDENT SEEDER")
    print("=" * 70)
    print()
    
    student_service = StudentService()
    students_data = generate_student_data()
    
    created_count = 0
    skipped_count = 0
    
    for student_data in students_data:
        student_id = student_data["student_id"]
        name = student_data["name"]
        
        # Check if student already exists
        if student_exists(student_service, student_id):
            print(f"⏭️  SKIPPED: {name} (UIN: {student_id}) - Already exists")
            skipped_count += 1
            continue
        
        # Get a random resume from the sample file
        resume_text = get_random_student_resume()
        
        # Prepare student data dictionary
        student_doc = {
            "student_id": student_id,
            "name": name,
            "email": student_data["email"],
            "major": student_data["major"],
            "grad_year": student_data["grad_year"],
            "interests": student_data["interests"],
            "skills": student_data["skills"],
            "resume_text": resume_text
        }
        
        # Create the student
        try:
            student_service.create_student(student_doc)
            print(f"✅ CREATED: {name} (UIN: {student_id}) - {student_data['major']} {student_data['grad_year']}")
            created_count += 1
        except Exception as e:
            print(f"❌ ERROR creating {name}: {str(e)}")
    
    print()
    print("=" * 70)
    print(f"SEEDING COMPLETE")
    print(f"  Created: {created_count} students")
    print(f"  Skipped: {skipped_count} students (already existed)")
    print(f"  Total:   {len(students_data)} students")
    print("=" * 70)


if __name__ == "__main__":
    seed_students()
