# CMIS Engagement Platform Admin Dashboard

A full-featured admin dashboard for the CMIS Engagement Platform built with Python, Streamlit, MongoDB, and Groq AI.

## Features

- 👨‍🎓 **Student Management**: Add, edit, and manage student profiles
- 👔 **Mentor Management**: Manage mentor profiles and availability
- 📅 **Event Management**: Create and manage events and workshops
- 🏆 **Case Competitions**: Organize and track case competitions
- 🤖 **AI-Powered Matching**: Intelligent student-mentor matching using Groq API
- 📧 **Email Management**: Send emails via N8N webhook with AI-generated content
- ⏰ **Task Scheduling**: Automated workflows and reminders

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.11
- **Database**: MongoDB (pymongo)
- **AI**: Groq API (LLaMA 3.1 / Mixtral models)
- **Email**: N8N webhook integration
- **PDF Processing**: pdfplumber
- **Scheduling**: APScheduler

## Project Structure

```
CMIS/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration and environment variables
├── db.py                       # MongoDB connection utilities
├── scheduler.py                # Task scheduling
├── requirements.txt            # Python dependencies
├── models/                     # Data models
│   ├── __init__.py
│   ├── students.py
│   ├── mentors.py
│   ├── events.py
│   ├── case_competitions.py
│   ├── matches.py
│   └── emails.py
├── services/                   # Business logic and database operations
│   ├── __init__.py
│   ├── student_service.py
│   ├── mentor_service.py
│   ├── event_service.py
│   ├── case_comp_service.py
│   ├── match_service.py
│   └── email_service.py
├── ai/                         # AI-powered features
│   ├── __init__.py
│   ├── matching.py            # Student-mentor matching algorithm
│   ├── email_generation.py    # AI email generation
│   └── workflow.py            # Automated workflows
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── pdf_utils.py           # PDF processing
│   └── time_utils.py          # Time and date utilities
└── sample_data/               # Sample data for testing
    ├── sample_student_resumes.txt
    └── sample_mentor_resumes.txt
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- MongoDB (local or cloud instance like MongoDB Atlas)
- Groq API key (get from https://console.groq.com)
- N8N instance with webhook configured (optional for email features)

### 2. Installation

1. Clone or download the project

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` file with your credentials:
```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=cmis_engagement
GROQ_API_KEY=your_groq_api_key_here
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
```

### 3. Run the Application

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Configuration

### MongoDB Setup

For local MongoDB:
```bash
# Install MongoDB (macOS)
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

For MongoDB Atlas (cloud):
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string and update `MONGODB_URI` in `.env`

### Groq API Setup

1. Sign up at https://console.groq.com
2. Create an API key
3. Add to `.env` file as `GROQ_API_KEY`

Available models:
- `llama-3.1-70b-versatile` (recommended for matching)
- `mixtral-8x7b-32768` (alternative option)

### N8N Email Setup (Optional)

1. Set up N8N instance (cloud or self-hosted)
2. Create webhook workflow for sending emails
3. Add webhook URL to `.env` as `N8N_WEBHOOK_URL`

## Usage

### Dashboard Pages

1. **Dashboard**: Overview of platform metrics and activity
2. **Students**: Manage student profiles and data
3. **Mentors**: Manage mentor profiles and availability
4. **Events**: Create and manage events
5. **Case Competitions**: Organize competitions
6. **Matching**: AI-powered student-mentor matching
7. **Email Management**: Send emails with AI generation

### AI Features

#### Student-Mentor Matching
- Navigate to "Matching" page
- Click "Run AI Matching Algorithm"
- System will analyze students and mentors
- Generate match scores with explanations
- Send notification emails automatically

#### AI Email Generation
- Navigate to "Email Management" page
- Select recipients and purpose
- Click "Generate with AI"
- Review and send AI-generated email

### API Usage

The services can also be used programmatically:

```python
from services.student_service import StudentService
from ai.matching import MatchingEngine

# Create student
student_service = StudentService()
# ... use service methods

# Run AI matching
matching_engine = MatchingEngine()
matches = matching_engine.find_best_matches(student, mentors, top_k=5)
```

## Data Models

### Student
- Personal info (name, email, major, year)
- Skills and interests
- Career goals
- Resume and LinkedIn links

### Mentor
- Professional info (company, job title)
- Expertise areas and industries
- Availability and mentoring capacity
- Years of experience

### Match
- Student-mentor pairing
- AI-generated match score (0-1)
- Match explanation
- Status (pending, accepted, active, completed)

### Event
- Event details (title, description, date)
- Location (physical or virtual)
- Registration tracking
- Capacity management

## Development

### Adding New Features

1. Create model in `models/`
2. Create service in `services/`
3. Add UI in `app.py`
4. Wire up in main navigation

### Testing

Use sample data provided in `sample_data/` directory for testing.

## Data Seeding and Testing

### 1. Seed Students (20 profiles)

```bash
python scripts/seed_students.py
```

This creates 20 diverse student profiles with:
- Majors: MIS, CSCE, CYBR, ISEN, STAT
- Graduation years: 2025-2027
- Realistic interests, skills, and resume text
- Idempotent (safe to run multiple times)

### 2. Test AI Matching Engine

```bash
python scripts/test_matching_engine.py
```

This script:
- Loads all mentors and students from database
- Runs AI matching for each student against all 7 mentors
- Displays top 3 matches with scores and AI-generated explanations
- Uses the hybrid scoring algorithm (40% interests, 40% skills, 20% resume similarity)
- Calls Groq Mixtral API for match reasoning

**Expected Output:**
```
=== MATCH RESULTS FOR: Sarah Chen ===
1. 👔 Mentor: Blaine Bryant | Score: 82.5%
   💡 Reason: Strong alignment in cloud architecture and distributed systems...
2. 👔 Mentor: Jeff Richardson | Score: 74.3%
3. 👔 Mentor: John Billings | Score: 63.8%
```

### Prerequisites

Before running these scripts, ensure:
1. MongoDB is running and connection is configured in `.env`
2. Mentors are seeded: `python scripts/seed_cmis_data.py`
3. Groq API key is set in `.env` (for AI reasoning)
4. Virtual environment is activated and dependencies are installed

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running
- Check connection string in `.env`
- Verify network access (for MongoDB Atlas)

### Groq API Errors
- Verify API key is correct
- Check API quota/limits
- Ensure internet connection

### Import Errors
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version (3.11+ required)

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or questions, please check:
- MongoDB documentation: https://docs.mongodb.com
- Streamlit documentation: https://docs.streamlit.io
- Groq API documentation: https://console.groq.com/docs

## Future Enhancements

- [ ] Add user authentication and authorization
- [ ] Implement file upload for bulk student/mentor import
- [ ] Add analytics and reporting dashboard
- [ ] Create mobile-responsive design
- [ ] Add calendar integration for events
- [ ] Implement real-time notifications
- [ ] Add chat functionality for matches
