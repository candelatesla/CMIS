"""
Test bulk CSV upload functionality
"""
import sys
sys.path.insert(0, '/Users/yashdoshi/Documents/CMIS')

import pandas as pd
from services.student_service import StudentService
from services.mentor_service import MentorService
from utils.pdf_utils import get_random_student_resume, get_random_mentor_resume


def test_student_bulk_upload():
    """Test student bulk CSV upload logic"""
    
    print("=" * 80)
    print("STUDENT BULK UPLOAD TEST")
    print("=" * 80)
    print()
    
    # Load CSV
    csv_path = "/Users/yashdoshi/Documents/CMIS/sample_data/sample_students.csv"
    df = pd.read_csv(csv_path)
    
    print(f"Loaded CSV with {len(df)} rows")
    print()
    print(df)
    print()
    
    # Initialize service
    student_service = StudentService()
    
    results = {
        "inserted": 0,
        "skipped": 0,
        "errors": []
    }
    
    # Process each row
    for idx, row in df.iterrows():
        print(f"Processing row {idx + 1}...")
        
        try:
            # Extract fields
            student_id = str(row.get('student_id', '')).strip()
            name = str(row.get('name', '')).strip()
            email = str(row.get('email', '')).strip()
            major = str(row.get('major', '')).strip()
            grad_year = int(row.get('grad_year', 2026))
            
            # Parse comma-separated fields
            interests_str = str(row.get('interests', ''))
            interests = [i.strip() for i in interests_str.split(',') if i.strip()] if interests_str and interests_str != 'nan' else []
            
            skills_str = str(row.get('skills', ''))
            skills = [s.strip() for s in skills_str.split(',') if s.strip()] if skills_str and skills_str != 'nan' else []
            
            resume_text = str(row.get('resume_text', ''))
            if not resume_text or resume_text == 'nan':
                resume_text = get_random_student_resume()
            
            print(f"  - Name: {name}")
            print(f"  - Email: {email}")
            print(f"  - Interests: {interests}")
            print(f"  - Skills: {skills}")
            
            # Check if exists
            existing = student_service.get_student_by_email(email)
            if existing:
                print(f"  ⏭️  Skipped (already exists)")
                results["skipped"] += 1
            else:
                # Create student
                student_data = {
                    "student_id": student_id,
                    "name": name,
                    "email": email,
                    "major": major,
                    "grad_year": grad_year,
                    "gpa": 3.5,
                    "interests": interests,
                    "skills": skills,
                    "resume_text": resume_text
                }
                
                result = student_service.create_student(student_data)
                
                if "error" in result:
                    print(f"  ❌ Error: {result['error']}")
                    results["errors"].append(f"{name}: {result['error']}")
                else:
                    print(f"  ✅ Inserted successfully")
                    results["inserted"] += 1
            
            print()
        
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results["errors"].append(f"Row {idx + 1}: {str(e)}")
            print()
    
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"✅ Inserted: {results['inserted']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    print(f"❌ Errors: {len(results['errors'])}")
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    print()


def test_mentor_bulk_upload():
    """Test mentor bulk CSV upload logic"""
    
    print("=" * 80)
    print("MENTOR BULK UPLOAD TEST")
    print("=" * 80)
    print()
    
    # Load CSV
    csv_path = "/Users/yashdoshi/Documents/CMIS/sample_data/sample_mentors.csv"
    df = pd.read_csv(csv_path)
    
    print(f"Loaded CSV with {len(df)} rows")
    print()
    print(df)
    print()
    
    # Initialize service
    mentor_service = MentorService()
    
    results = {
        "inserted": 0,
        "skipped": 0,
        "errors": []
    }
    
    # Process each row
    for idx, row in df.iterrows():
        print(f"Processing row {idx + 1}...")
        
        try:
            # Extract fields
            mentor_id = str(row.get('mentor_id', '')).strip()
            name = str(row.get('name', '')).strip()
            email = str(row.get('email', '')).strip()
            company = str(row.get('company', '')).strip()
            job_title = str(row.get('job_title', '')).strip()
            industry = str(row.get('industry', '')).strip()
            max_mentees = int(row.get('max_mentees', 3))
            
            # Parse comma-separated fields
            expertise_str = str(row.get('expertise_areas', ''))
            expertise_areas = [e.strip() for e in expertise_str.split(',') if e.strip()] if expertise_str and expertise_str != 'nan' else []
            
            interests_str = str(row.get('interests', ''))
            interests = [i.strip() for i in interests_str.split(',') if i.strip()] if interests_str and interests_str != 'nan' else []
            
            resume_text = str(row.get('resume_text', ''))
            if not resume_text or resume_text == 'nan':
                resume_text = get_random_mentor_resume()
            
            print(f"  - Name: {name}")
            print(f"  - Email: {email}")
            print(f"  - Expertise: {expertise_areas}")
            print(f"  - Interests: {interests}")
            
            # Check if exists
            existing = mentor_service.get_mentor_by_email(email)
            if existing:
                print(f"  ⏭️  Skipped (already exists)")
                results["skipped"] += 1
            else:
                # Create mentor
                mentor_data = {
                    "mentor_id": mentor_id,
                    "name": name,
                    "email": email,
                    "company": company,
                    "job_title": job_title,
                    "industry": industry,
                    "years_experience": 5,
                    "expertise_areas": expertise_areas,
                    "interests": interests,
                    "max_mentees": max_mentees,
                    "current_mentees": 0,
                    "resume_text": resume_text
                }
                
                result = mentor_service.create_mentor(mentor_data)
                
                if "error" in result:
                    print(f"  ❌ Error: {result['error']}")
                    results["errors"].append(f"{name}: {result['error']}")
                else:
                    print(f"  ✅ Inserted successfully")
                    results["inserted"] += 1
            
            print()
        
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results["errors"].append(f"Row {idx + 1}: {str(e)}")
            print()
    
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"✅ Inserted: {results['inserted']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    print(f"❌ Errors: {len(results['errors'])}")
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    print()


if __name__ == "__main__":
    test_student_bulk_upload()
    print("\n\n")
    test_mentor_bulk_upload()
