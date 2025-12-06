# CMIS Engagement Platform

A full-featured engagement platform for the CMIS program at Texas A&M University, featuring AI-powered student-mentor matching, event management, and automated workflows. Built with Python, Streamlit, MongoDB, and Groq AI.

## 🏆 Competition Achievement

**2nd Place Overall** - 2025 CMIS Case Competition at Texas A&M University

Recognized for:
- Exceptional technical implementation
- End-to-end automation
- AI-powered matching engine
- Advanced workflow orchestration via N8N
- Clean UI and robust role-based dashboards

## ✨ Features

### Admin Dashboard
- 👨‍🎓 **Student Management**: Add, edit, and manage student profiles
- 👔 **Mentor Management**: Manage mentor profiles and availability
- 📅 **Event Management**: Create and manage events and workshops
- 🏆 **Case Competitions**: Organize and track case competitions
- 🤖 **AI-Powered Matching**: Intelligent student-mentor matching using Groq API
- 📧 **Email Management**: Send emails via N8N webhook with AI-generated content
- ⏰ **Task Scheduling**: Automated workflows and reminders
- ⚡ **Instant Demo Mode**: Create mentor requests instantly for presentations

### Student Dashboard
- ✏️ Edit complete profile (name, major, UIN, skills, interests, contact)
- 📄 Upload and version resumes (automatic version control)
- 📅 Register for events and create teams
- 👔 View assigned mentors after acceptance
- 🏅 View team scores after judge evaluations
- 📧 Receive automated HTML-formatted emails for mentorship, registration, and scoring

### Mentor/Judge Dashboard
- 📋 View pending mentorship requests from AI matching
- 👤 Review student profiles, resumes, skills, and match explanations
- ✅ Accept or decline mentorship requests
- 📊 View assigned events and teams for judging
- 💯 Enter scores and comments for team evaluations
- 📧 Instant email notifications for all actions

## 🔄 Key Workflows

### Mentorship Acceptance Workflow
1. Admin runs AI matching algorithm
2. Pending mentorship requests created (supports Instant Mode)
3. Mentor logs in and views pending requests
4. Mentor accepts/declines request
5. Automated emails sent to both student and mentor
6. Student dashboard updates with mentor details
7. All updates reflect instantly

### Judge Scoring Workflow
1. Admins assign judges to events
2. Teams register for events
3. Admin assigns teams to judges (randomized distribution)
4. Judges view assigned teams and enter scores (0-100) with comments
5. Scores saved and students notified via email
6. Real-time updates across all dashboards

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **Database**: MongoDB Atlas (pymongo)
- **AI**: Groq API (LLaMA 3.1 / Mixtral models)
- **Email Automation**: N8N webhook integration
- **PDF Processing**: pdfplumber

## 📁 Project Structure

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
└── utils/                      # Utility functions
    ├── __init__.py
    ├── pdf_utils.py           # PDF processing
    └── time_utils.py          # Time and date utilities
```

## 📊 Data Models

### Student
- Personal info (name, email, UIN, major, graduation year)
- Skills and interests
- Career goals
- Resume versions and LinkedIn profile
- Team registrations and scores

### Mentor
- Professional info (company, job title, years of experience)
- Expertise areas and industries
- Availability and mentoring capacity
- Judge assignments

### Match
- Student-mentor pairing
- AI-generated match score (0-100%)
- Detailed match explanation from Groq AI
- Status (pending, accepted, active, completed)

### Event
- Event details (title, description, date, location)
- Registration tracking and team management
- Judge assignments
- Capacity management

### Team
- Team name and members
- Event registration
- Judge assignments and scores
- Comments and feedback

## 🤖 AI Features

### Student-Mentor Matching Algorithm

The hybrid scoring algorithm uses:
- **40% Interest Alignment**: Matching career goals and interests
- **40% Skills Match**: Technical and soft skills compatibility
- **20% Resume Similarity**: NLP-based text analysis

#### Running AI Matching

Navigate to "Matching" page in the Admin Dashboard, click "Run AI Matching Algorithm", and the system will:
1. Analyze all students and mentors
2. Generate match scores with AI explanations
3. Create pending mentorship requests
4. Send notification emails automatically

### AI Email Generation

1. Navigate to "Email Management" page
2. Select recipients and email purpose
3. Click "Generate with AI"
4. Review AI-generated HTML email
5. Send with one click

## 🎯 System Architecture

```
┌─────────────────┐          ┌────────────────┐
│   Student UI     │          │   Mentor UI     │
│ (Streamlit App)  │          │ (Judge UI)      │
└─────────┬────────┘          └────────┬────────┘
          │                             │
          ▼                             ▼
     Student Service               Mentor/Judge Service
          │                             │
          ├──────────────┬──────────────┤
          ▼              ▼              ▼
     Matching Engine   Team Service   Event Service
     (Groq AI API)                         │
          │                                 │
          ▼                                 ▼
     Mentor Matching                 Judge Assignment
          │                                 │
          └──────────┬───────────┬─────────┘
                     ▼           ▼
               MongoDB Atlas   N8N Webhook
                     │           │
                     ▼           ▼
              Data Persistence   Automated Emails
```

## 🔧 Development

### Adding New Features

1. Create data model in `models/`
2. Create service class in `services/`
3. Add UI components in `app.py`
4. Wire up in main navigation

### API Usage

Services can be used programmatically:

```python
from services.student_service import StudentService
from ai.matching import MatchingEngine

# Create student
student_service = StudentService()
student = student_service.create_student({
    "name": "John Doe",
    "email": "john@tamu.edu",
    "major": "MIS"
})

# Run AI matching
matching_engine = MatchingEngine()
mentors = mentor_service.get_all_mentors()
matches = matching_engine.find_best_matches(student, mentors, top_k=5)
```

## 🔮 Future Enhancements

- [ ] User authentication and role-based authorization
- [ ] Bulk import via CSV/Excel for students and mentors
- [ ] Advanced analytics and reporting dashboard
- [ ] Mobile-responsive design improvements
- [ ] Calendar integration for events (Google Calendar, Outlook)
- [ ] Real-time notifications (WebSocket/Server-Sent Events)
- [ ] In-app chat functionality for mentor-student communication
- [ ] Export reports to PDF
- [ ] Integration with university systems (Banner, Canvas)
- [ ] Multi-language support

## 📄 License

MIT License - feel free to use and modify for your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👥 Team

Developed for the CMIS Case Competition at Texas A&M University.
Team Members: Yash Doshi, Khushi Shah, Chintan Shah & Ujjawal Patel

## 📧 Support

For issues or questions, open an issue on GitHub or check the documentation links above.
