# CMIS Database Seeding Script

## Overview
This script populates the MongoDB database with seed data for the CMIS Case Competition Platform.

## What Gets Seeded

### 1. Mentors (7 total)
- **Blaine Bryant** - Chief Information Security Officer at VMware
- **Jeff Richardson** - Director of Engineering at Amazon Web Services
- **Nikhil Gupta** - Lead Cloud Architect at Red Hat
- **Mahidhar Panyam** - Director of Data Engineering at Accenture
- **Suryakant Kaushik** - Lead Cloud Architect at Google Cloud
- **John Billings** - VP of Technology at Google Cloud
- **Divyesh Batra** - Senior Data Engineer at Visa Inc

Each mentor includes:
- Auto-generated email, mentor_id, company, job_title
- Industry classification
- 4-6 expertise areas
- 3-5 interests
- Random max_mentees (2-6)
- Resume text from sample data

### 2. Event
- **Name:** CMIS Fall Case Competition 2025
- **Event ID:** cmis_fall_case_comp_2025
- **Date:** December 5, 2025 (9:00 AM - 5:00 PM CST)
- **Location:** Mays Business School, Texas A&M University
- **Capacity:** 200 students
- **Sponsor:** ExaByte

### 3. Case Competition
- **Name:** CMIS AI Strategy Case Competition
- **Competition ID:** cmis_comp_2025
- **Team Size:** 2-4 members
- **Judges:** All 7 mentors listed above
- **Prizes:** 1st: $5000, 2nd: $3000, 3rd: $1500

## Usage

### Run the seed script:
```bash
python scripts/seed_cmis_data.py
```

Or using the virtual environment directly:
```bash
/Users/yashdoshi/Documents/CMIS/.venv/bin/python scripts/seed_cmis_data.py
```

## Features

### ✅ Idempotent
The script can be run multiple times safely:
- Skips existing mentors (checks by name and email)
- Skips existing events (checks by event_id)
- Skips existing competitions (checks by competition_id)
- Only adds judges that aren't already in the list

### 📊 Clear Logging
Every operation is logged:
- `[OK]` - Successfully created new record
- `[SKIP]` - Record already exists
- `[ERROR]` - Operation failed (with error details)

### 🔄 Safe Execution
- No data is deleted or overwritten
- Uses service layer for all database operations
- Validates data before insertion
- Comprehensive error handling

## Output Example

```
============================================================
CMIS CASE COMPETITION PLATFORM - DATABASE SEEDING
============================================================
Started at: 2025-12-03 18:57:25

============================================================
SEEDING MENTORS
============================================================
[OK] Mentor 'Blaine Bryant' created - Chief Information Security Officer at VMware
[OK] Mentor 'Jeff Richardson' created - Director of Engineering at Amazon Web Services
...

✅ Mentors: 6 created, 1 skipped

============================================================
SEEDING EVENT
============================================================
[OK] Event 'CMIS Fall Case Competition 2025' created
     Location: Mays Business School, Texas A&M University
     Date: December 5, 2025
     Capacity: 200

============================================================
SEEDING CASE COMPETITION & JUDGES
============================================================
[OK] Competition 'CMIS AI Strategy Case Competition' created
[OK] Added 7 judges to competition

✅ Competition: 1 updated with 7 judges

============================================================
SEEDING COMPLETE
============================================================
Mentors:      6 created, 1 skipped
Events:       1 created, 0 skipped
Competitions: 1 created, 0 skipped
Judges:       7 names added to competition

✅ Database seeding successful!
💡 View results in Streamlit: http://localhost:8506
```

## Verification

After running the seed script, verify the data in:
- **Streamlit UI:** http://localhost:8506
  - Navigate to "Mentors" page to see all 7 mentors
  - Navigate to "Events" page to see the case competition event
  - Navigate to "Case Competitions" page to see the competition with judges

## Sample Data Files

The script uses sample resume data from:
- `/sample_data/sample_mentor_resumes.txt` - 10 diverse mentor resume samples
  - Now includes 5 additional senior-level resumes for:
    - Thomas Anderson (Cloud Architect)
    - Priya Sharma (Cybersecurity Director)
    - Marcus Williams (Lead Data Scientist)
    - Rachel Kim (VP of Engineering)
    - And others...

## Customization

To modify the seed data, edit these sections in `scripts/seed_cmis_data.py`:

1. **MENTOR_NAMES** - List of mentor names to create
2. **COMPANIES** - Pool of companies for random assignment
3. **JOB_TITLES** - Pool of job titles for random assignment
4. **EXPERTISE_POOL** - Pool of expertise areas
5. **INTERESTS_POOL** - Pool of interests

For event/competition details, modify the dictionaries in:
- `seed_event()` function
- `seed_competition_and_judges()` function

## Dependencies

The script uses these services:
- `services.mentor_service.MentorService`
- `services.event_service.EventService`
- `services.case_comp_service.CaseCompService`
- `utils.pdf_utils.get_random_mentor_resume`

## Troubleshooting

**MongoDB connection error:**
- Ensure MongoDB is running
- Check `.env` file for correct `MONGODB_URI`

**Import errors:**
- Ensure you're in the project root directory
- Use the virtual environment: `source .venv/bin/activate`

**Duplicate data:**
- The script is idempotent and will skip existing records
- To reset, delete records from MongoDB manually or use MongoDB Compass

## Future Enhancements

Potential additions:
- [ ] Seed student data
- [ ] Seed mentor-student matches
- [ ] Seed team registrations for competitions
- [ ] Add command-line arguments for selective seeding
- [ ] Add `--reset` flag to clear existing data before seeding
