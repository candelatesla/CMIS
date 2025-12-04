"""
CMIS Engagement Platform Admin Dashboard
Main Streamlit application entry point
"""
import streamlit as st
import pandas as pd
import random
from datetime import datetime
from config import APP_TITLE, APP_VERSION, validate_config
from db import get_database
from scheduler import scheduler

# Services imports
from services.student_service import StudentService
from services.mentor_service import MentorService
from services.event_service import EventService
from services.case_comp_service import CaseCompService
from services.match_service import MatchService
from services.email_service import EmailService

# Utils imports
from utils.pdf_utils import extract_text_from_pdf, get_random_student_resume, get_random_mentor_resume


def init_app():
    """Initialize the application"""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Validate configuration
    if not validate_config():
        st.error("⚠️ Missing required environment variables. Please check your .env file.")
        st.stop()
    
    # Initialize database connection
    try:
        get_database()
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        st.stop()


def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.title("🎓 CMIS Dashboard")
        st.caption(f"Version {APP_VERSION}")
        st.divider()
        
        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Students",
                "Mentors",
                "Events",
                "Case Competitions",
                "Matching",
                "Email Management"
            ]
        )
        
        st.divider()
        st.caption("Admin Tools")
        
        return page


def render_dashboard():
    """Render the main dashboard page"""
    st.title("📊 Dashboard Overview")
    
    # Initialize services
    student_service = StudentService()
    mentor_service = MentorService()
    event_service = EventService()
    match_service = MatchService()
    
    # Get counts
    students = student_service.list_students()
    mentors = mentor_service.list_mentors()
    events = event_service.list_events()
    matches = match_service.list_matches({"status": "active"})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(students))
    
    with col2:
        st.metric("Total Mentors", len(mentors))
    
    with col3:
        st.metric("Total Events", len(events))
    
    with col4:
        st.metric("Active Matches", len(matches))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Students")
        if students:
            recent_students = sorted(students, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            for student in recent_students:
                st.write(f"👤 **{student.get('name', 'Unknown')}** - {student.get('major', 'N/A')}")
        else:
            st.info("No students registered yet")
    
    with col2:
        st.subheader("Recent Mentors")
        if mentors:
            recent_mentors = sorted(mentors, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            for mentor in recent_mentors:
                st.write(f"👔 **{mentor.get('name', 'Unknown')}** - {mentor.get('company', 'N/A')}")
        else:
            st.info("No mentors registered yet")


def render_students_page():
    """Render the students management page with full CRUD"""
    st.title("👨‍🎓 Student Management")
    
    # Initialize service
    student_service = StudentService()
    
    # Add New Student Section (at top)
    with st.expander("➕ Add New Student", expanded=False):
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="John Smith")
                email = st.text_input("Email *", placeholder="john.smith@university.edu")
                student_id = st.text_input("Student ID *", placeholder="STU001")
                major = st.text_input("Major *", placeholder="Computer Science")
                
            with col2:
                grad_year = st.number_input("Graduation Year *", min_value=2024, max_value=2030, value=2026)
                gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, value=3.5, step=0.1)
                interests = st.text_input("Interests (comma-separated)", placeholder="AI, Web Dev, Data Science")
                skills = st.text_input("Skills (comma-separated)", placeholder="Python, Java, React")
            
            # Resume upload
            st.subheader("Resume")
            uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="student_resume")
            use_sample = st.checkbox("Use sample resume if no file uploaded")
            
            submitted = st.form_submit_button("Add Student", type="primary")
            
            if submitted:
                if not all([name, email, student_id, major]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    # Handle resume
                    resume_text = ""
                    if uploaded_resume:
                        try:
                            resume_text = extract_text_from_pdf(uploaded_resume)
                            st.success("✅ Resume uploaded and parsed successfully!")
                        except Exception as e:
                            st.warning(f"Could not parse resume: {str(e)}")
                    elif use_sample:
                        # Load random sample resume
                        try:
                            resume_text = get_random_student_resume()
                            st.info("📄 Using sample student resume")
                        except Exception as e:
                            st.warning(f"Could not load sample resume: {str(e)}")
                    
                    # Create student data
                    student_data = {
                        "name": name,
                        "email": email,
                        "student_id": student_id,
                        "major": major,
                        "grad_year": grad_year,
                        "gpa": gpa,
                        "interests": [i.strip() for i in interests.split(",") if i.strip()],
                        "skills": [s.strip() for s in skills.split(",") if s.strip()],
                        "resume_text": resume_text
                    }
                    
                    # Create student
                    result = student_service.create_student(student_data)
                    
                    if "error" in result:
                        st.error(f"Error creating student: {result['error']}")
                    else:
                        st.success(f"✅ Student '{name}' added successfully!")
                        st.rerun()
    
    st.divider()
    
    # Search and Filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search students", placeholder="Search by name, email, major, or student ID...")
    with col2:
        st.write("")  # Spacing
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Get all students
    students = student_service.list_students()
    
    if not students:
        st.info("📭 No students registered yet. Add your first student above!")
    else:
        # Client-side filtering
        if search_query:
            filtered_students = [
                s for s in students
                if search_query.lower() in s.get("name", "").lower()
                or search_query.lower() in s.get("email", "").lower()
                or search_query.lower() in s.get("major", "").lower()
                or search_query.lower() in s.get("student_id", "").lower()
            ]
        else:
            filtered_students = students
        
        st.write(f"**Total Students:** {len(filtered_students)} {f'(filtered from {len(students)})' if search_query else ''}")
        
        # Display students in table format with expandable details
        for idx, student in enumerate(filtered_students):
            with st.expander(f"👤 {student.get('name', 'Unknown')} - {student.get('student_id', 'N/A')} - {student.get('major', 'N/A')}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write("**Basic Information**")
                    st.write(f"**Name:** {student.get('name', 'N/A')}")
                    st.write(f"**Email:** {student.get('email', 'N/A')}")
                    st.write(f"**Student ID:** {student.get('student_id', 'N/A')}")
                    st.write(f"**Major:** {student.get('major', 'N/A')}")
                
                with col2:
                    st.write("**Academic Details**")
                    st.write(f"**Graduation Year:** {student.get('grad_year', 'N/A')}")
                    st.write(f"**GPA:** {student.get('gpa', 'N/A')}")
                    st.write(f"**Interests:** {', '.join(student.get('interests', [])) or 'None'}")
                    st.write(f"**Skills:** {', '.join(student.get('skills', [])) or 'None'}")
                
                with col3:
                    st.write("**Actions**")
                    edit_key = f"edit_student_{student.get('_id', idx)}"
                    delete_key = f"delete_student_{student.get('_id', idx)}"
                    
                    if st.button("✏️ Edit", key=edit_key, use_container_width=True):
                        st.session_state[f"editing_{student['_id']}"] = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=delete_key, type="secondary", use_container_width=True):
                        st.session_state[f"confirm_delete_{student['_id']}"] = True
                        st.rerun()
                
                # Resume section (show/hide without nested expander)
                if student.get("resume_text"):
                    st.divider()
                    st.markdown("**📄 Resume Content:**")
                    st.text_area("", student["resume_text"], height=150, disabled=True, key=f"resume_text_{student.get('_id', idx)}", label_visibility="collapsed")
                
                # Edit form (inline)
                if st.session_state.get(f"editing_{student['_id']}", False):
                    st.divider()
                    st.subheader("Edit Student")
                    
                    with st.form(f"edit_form_{student['_id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Full Name", value=student.get('name', ''))
                            edit_email = st.text_input("Email", value=student.get('email', ''))
                            edit_major = st.text_input("Major", value=student.get('major', ''))
                            edit_grad_year = st.number_input("Graduation Year", min_value=2024, max_value=2030, value=student.get('grad_year', 2026))
                        
                        with col2:
                            edit_gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, value=float(student.get('gpa', 3.5)), step=0.1)
                            edit_interests = st.text_input("Interests (comma-separated)", value=", ".join(student.get('interests', [])))
                            edit_skills = st.text_input("Skills (comma-separated)", value=", ".join(student.get('skills', [])))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                updates = {
                                    "name": edit_name,
                                    "email": edit_email,
                                    "major": edit_major,
                                    "grad_year": edit_grad_year,
                                    "gpa": edit_gpa,
                                    "interests": [i.strip() for i in edit_interests.split(",") if i.strip()],
                                    "skills": [s.strip() for s in edit_skills.split(",") if s.strip()]
                                }
                                
                                result = student_service.update_student(student['_id'], updates)
                                
                                if "error" in result:
                                    st.error(f"Error updating student: {result['error']}")
                                else:
                                    st.success("✅ Student updated successfully!")
                                    del st.session_state[f"editing_{student['_id']}"]
                                    st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                del st.session_state[f"editing_{student['_id']}"]
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_{student['_id']}", False):
                    st.divider()
                    st.warning(f"⚠️ Are you sure you want to delete **{student.get('name', 'this student')}**? This action cannot be undone.")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_yes_{student['_id']}", type="primary"):
                            result = student_service.delete_student(student['_id'])
                            
                            if "error" in result:
                                st.error(f"Error deleting student: {result['error']}")
                            else:
                                st.success(f"✅ Student '{student.get('name', 'Unknown')}' deleted successfully!")
                                del st.session_state[f"confirm_delete_{student['_id']}"]
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"confirm_no_{student['_id']}"):
                            del st.session_state[f"confirm_delete_{student['_id']}"]
                            st.rerun()



def render_mentors_page():
    """Render the mentors management page with full CRUD"""
    st.title("👔 Mentor Management")
    
    # Initialize service
    mentor_service = MentorService()
    
    # Add New Mentor Section (at top)
    with st.expander("➕ Add New Mentor", expanded=False):
        with st.form("add_mentor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="Sarah Johnson")
                email = st.text_input("Email *", placeholder="sarah.johnson@company.com")
                mentor_id = st.text_input("Mentor ID *", placeholder="MEN001")
                company = st.text_input("Company *", placeholder="Tech Solutions Corp")
                
            with col2:
                job_title = st.text_input("Job Title *", placeholder="Senior Software Engineer")
                industry = st.text_input("Industry *", placeholder="Technology")
                years_experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=5)
                max_mentees = st.number_input("Max Mentees", min_value=1, max_value=20, value=3)
            
            expertise_areas = st.text_input("Expertise Areas (comma-separated)", placeholder="Software Architecture, Cloud Computing, Machine Learning")
            linkedin_url = st.text_input("LinkedIn URL (optional)", placeholder="https://linkedin.com/in/username")
            
            # Resume upload
            st.subheader("Resume/Bio")
            uploaded_resume = st.file_uploader("Upload Resume/Bio (PDF)", type=["pdf"], key="mentor_resume")
            use_sample = st.checkbox("Use sample resume if no file uploaded")
            
            submitted = st.form_submit_button("Add Mentor", type="primary")
            
            if submitted:
                if not all([name, email, mentor_id, company, job_title, industry]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    # Handle resume
                    resume_text = ""
                    if uploaded_resume:
                        try:
                            resume_text = extract_text_from_pdf(uploaded_resume)
                            st.success("✅ Resume uploaded and parsed successfully!")
                        except Exception as e:
                            st.warning(f"Could not parse resume: {str(e)}")
                    elif use_sample:
                        # Load random sample resume
                        try:
                            resume_text = get_random_mentor_resume()
                            st.info("📄 Using sample mentor resume")
                        except Exception as e:
                            st.warning(f"Could not load sample resume: {str(e)}")
                    
                    # Create mentor data
                    mentor_data = {
                        "name": name,
                        "email": email,
                        "mentor_id": mentor_id,
                        "company": company,
                        "job_title": job_title,
                        "industry": industry,
                        "years_experience": years_experience,
                        "expertise_areas": [e.strip() for e in expertise_areas.split(",") if e.strip()],
                        "max_mentees": max_mentees,
                        "current_mentees": 0,
                        "linkedin_url": linkedin_url if linkedin_url else None,
                        "resume_text": resume_text
                    }
                    
                    # Create mentor
                    result = mentor_service.create_mentor(mentor_data)
                    
                    if "error" in result:
                        st.error(f"Error creating mentor: {result['error']}")
                    else:
                        st.success(f"✅ Mentor '{name}' added successfully!")
                        st.rerun()
    
    st.divider()
    
    # Search and Filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search mentors", placeholder="Search by name, email, company, or mentor ID...")
    with col2:
        st.write("")  # Spacing
    with col3:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_mentors"):
            st.rerun()
    
    # Get all mentors
    mentors = mentor_service.list_mentors()
    
    if not mentors:
        st.info("📭 No mentors registered yet. Add your first mentor above!")
    else:
        # Client-side filtering
        if search_query:
            filtered_mentors = [
                m for m in mentors
                if search_query.lower() in m.get("name", "").lower()
                or search_query.lower() in m.get("email", "").lower()
                or search_query.lower() in m.get("company", "").lower()
                or search_query.lower() in m.get("mentor_id", "").lower()
            ]
        else:
            filtered_mentors = mentors
        
        st.write(f"**Total Mentors:** {len(filtered_mentors)} {f'(filtered from {len(mentors)})' if search_query else ''}")
        
        # Display mentors in table format with expandable details
        for idx, mentor in enumerate(filtered_mentors):
            # Calculate capacity
            current = mentor.get('current_mentees', 0)
            max_cap = mentor.get('max_mentees', 3)
            capacity_pct = (current / max_cap * 100) if max_cap > 0 else 0
            capacity_color = "🟢" if capacity_pct < 70 else "🟡" if capacity_pct < 100 else "🔴"
            
            with st.expander(f"👤 {mentor.get('name', 'Unknown')} - {mentor.get('company', 'N/A')} - {mentor.get('job_title', 'N/A')} {capacity_color} ({current}/{max_cap})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write("**Basic Information**")
                    st.write(f"**Name:** {mentor.get('name', 'N/A')}")
                    st.write(f"**Email:** {mentor.get('email', 'N/A')}")
                    st.write(f"**Mentor ID:** {mentor.get('mentor_id', 'N/A')}")
                    st.write(f"**Company:** {mentor.get('company', 'N/A')}")
                    st.write(f"**Job Title:** {mentor.get('job_title', 'N/A')}")
                
                with col2:
                    st.write("**Professional Details**")
                    st.write(f"**Industry:** {mentor.get('industry', 'N/A')}")
                    st.write(f"**Years of Experience:** {mentor.get('years_experience', 'N/A')}")
                    st.write(f"**Expertise:** {', '.join(mentor.get('expertise_areas', [])) or 'None'}")
                    st.write(f"**Capacity:** {current}/{max_cap} mentees")
                    if mentor.get('linkedin_url'):
                        st.write(f"**LinkedIn:** [{mentor['linkedin_url']}]({mentor['linkedin_url']})")
                
                with col3:
                    st.write("**Actions**")
                    edit_key = f"edit_mentor_{mentor.get('_id', idx)}"
                    delete_key = f"delete_mentor_{mentor.get('_id', idx)}"
                    
                    if st.button("✏️ Edit", key=edit_key, use_container_width=True):
                        st.session_state[f"editing_mentor_{mentor['_id']}"] = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=delete_key, type="secondary", use_container_width=True):
                        st.session_state[f"confirm_delete_mentor_{mentor['_id']}"] = True
                        st.rerun()
                
                # Resume section (show without nested expander)
                if mentor.get("resume_text"):
                    st.divider()
                    st.markdown("**📄 Resume/Bio Content:**")
                    st.text_area("", mentor["resume_text"], height=150, disabled=True, key=f"resume_text_mentor_{mentor.get('_id', idx)}", label_visibility="collapsed")
                
                # Edit form (inline)
                if st.session_state.get(f"editing_mentor_{mentor['_id']}", False):
                    st.divider()
                    st.subheader("Edit Mentor")
                    
                    with st.form(f"edit_form_mentor_{mentor['_id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Full Name", value=mentor.get('name', ''))
                            edit_email = st.text_input("Email", value=mentor.get('email', ''))
                            edit_company = st.text_input("Company", value=mentor.get('company', ''))
                            edit_job_title = st.text_input("Job Title", value=mentor.get('job_title', ''))
                        
                        with col2:
                            edit_industry = st.text_input("Industry", value=mentor.get('industry', ''))
                            edit_years = st.number_input("Years of Experience", min_value=0, max_value=50, value=mentor.get('years_experience', 5))
                            edit_max_mentees = st.number_input("Max Mentees", min_value=1, max_value=20, value=mentor.get('max_mentees', 3))
                            edit_expertise = st.text_input("Expertise Areas (comma-separated)", value=", ".join(mentor.get('expertise_areas', [])))
                        
                        edit_linkedin = st.text_input("LinkedIn URL", value=mentor.get('linkedin_url', ''))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                updates = {
                                    "name": edit_name,
                                    "email": edit_email,
                                    "company": edit_company,
                                    "job_title": edit_job_title,
                                    "industry": edit_industry,
                                    "years_experience": edit_years,
                                    "max_mentees": edit_max_mentees,
                                    "expertise_areas": [e.strip() for e in edit_expertise.split(",") if e.strip()],
                                    "linkedin_url": edit_linkedin if edit_linkedin else None
                                }
                                
                                result = mentor_service.update_mentor(mentor['_id'], updates)
                                
                                if "error" in result:
                                    st.error(f"Error updating mentor: {result['error']}")
                                else:
                                    st.success("✅ Mentor updated successfully!")
                                    del st.session_state[f"editing_mentor_{mentor['_id']}"]
                                    st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                del st.session_state[f"editing_mentor_{mentor['_id']}"]
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_mentor_{mentor['_id']}", False):
                    st.divider()
                    st.warning(f"⚠️ Are you sure you want to delete **{mentor.get('name', 'this mentor')}**? This action cannot be undone.")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_yes_mentor_{mentor['_id']}", type="primary"):
                            result = mentor_service.delete_mentor(mentor['_id'])
                            
                            if "error" in result:
                                st.error(f"Error deleting mentor: {result['error']}")
                            else:
                                st.success(f"✅ Mentor '{mentor.get('name', 'Unknown')}' deleted successfully!")
                                del st.session_state[f"confirm_delete_mentor_{mentor['_id']}"]
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"confirm_no_mentor_{mentor['_id']}"):
                            del st.session_state[f"confirm_delete_mentor_{mentor['_id']}"]
                            st.rerun()



def render_events_page():
    """Render the events management page with full CRUD"""
    st.title("📅 Event Management")
    
    # Initialize service
    event_service = EventService()
    
    # Add New Event Section (at top)
    with st.expander("➕ Create New Event", expanded=False):
        with st.form("create_event_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                event_title = st.text_input("Event Title *", placeholder="Annual Career Fair")
                event_id = st.text_input("Event ID *", placeholder="EVT001")
                event_type = st.selectbox("Event Type *", [
                    "Career Fair",
                    "Networking",
                    "Workshop",
                    "Conference",
                    "Seminar",
                    "Social Event",
                    "Other"
                ])
                location = st.text_input("Location *", placeholder="Student Center, Room 101")
            
            with col2:
                start_date = st.date_input("Start Date *")
                start_time = st.time_input("Start Time *")
                end_date = st.date_input("End Date *")
                end_time = st.time_input("End Time *")
            
            description = st.text_area("Description", placeholder="Event details and agenda...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                capacity = st.number_input("Capacity", min_value=0, value=100, help="0 = unlimited")
            with col2:
                registration_required = st.checkbox("Registration Required", value=True)
            with col3:
                sponsor_tier = st.selectbox("Sponsor Tier", ["None", "Bronze", "Silver", "Gold", "Platinum"])
            
            submitted = st.form_submit_button("Create Event", type="primary")
            
            if submitted:
                if not all([event_title, event_id, event_type, location]):
                    st.error("Please fill in all required fields marked with *")
                else:
                    # Combine date and time into datetime
                    from datetime import datetime, timezone
                    start_datetime = datetime.combine(start_date, start_time).replace(tzinfo=timezone.utc)
                    end_datetime = datetime.combine(end_date, end_time).replace(tzinfo=timezone.utc)
                    
                    # Validate dates
                    if end_datetime <= start_datetime:
                        st.error("End date/time must be after start date/time")
                    else:
                        # Create event data
                        event_data = {
                            "event_id": event_id,
                            "name": event_title,
                            "event_type": event_type,
                            "description": description if description else "",
                            "start_datetime": start_datetime,
                            "end_datetime": end_datetime,
                            "location": location,
                            "capacity": capacity if capacity > 0 else None,
                            "registered_count": 0,
                            "registration_required": registration_required,
                            "sponsor_tier": sponsor_tier if sponsor_tier != "None" else None
                        }
                        
                        # Create event
                        result = event_service.create_event(event_data)
                        
                        if "error" in result:
                            st.error(f"Error creating event: {result['error']}")
                        else:
                            st.success(f"✅ Event '{event_title}' created successfully!")
                            st.rerun()
    
    st.divider()
    
    # Search and Filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search events", placeholder="Search by title, location, or event ID...")
    with col2:
        event_filter = st.selectbox("Filter", ["All", "Upcoming", "Past"])
    with col3:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_events"):
            st.rerun()
    
    # Get events based on filter
    if event_filter == "Upcoming":
        events = event_service.get_upcoming_events(limit=100)
    else:
        events = event_service.list_events()
        
        # Filter past events if needed
        if event_filter == "Past":
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            events = [e for e in events if datetime.fromisoformat(e.get('start_datetime', '')) < now]
    
    if not events:
        st.info("📭 No events found. Create your first event above!")
    else:
        # Client-side filtering by search
        if search_query:
            filtered_events = [
                e for e in events
                if search_query.lower() in e.get("name", "").lower()
                or search_query.lower() in e.get("location", "").lower()
                or search_query.lower() in e.get("event_id", "").lower()
            ]
        else:
            filtered_events = events
        
        st.write(f"**Total Events:** {len(filtered_events)} {f'(filtered from {len(events)})' if search_query else ''}")
        
        # Display events in expandable cards
        for idx, event in enumerate(filtered_events):
            # Format dates
            from datetime import datetime
            try:
                start_dt = datetime.fromisoformat(event.get('start_datetime', ''))
                end_dt = datetime.fromisoformat(event.get('end_datetime', ''))
                start_str = start_dt.strftime("%b %d, %Y at %I:%M %p")
                end_str = end_dt.strftime("%b %d, %Y at %I:%M %p")
                
                # Check if event is upcoming or past
                from datetime import timezone
                now = datetime.now(timezone.utc)
                status_icon = "🟢" if start_dt > now else "🔴"
                status_text = "Upcoming" if start_dt > now else "Past"
            except:
                start_str = "N/A"
                end_str = "N/A"
                status_icon = "⚪"
                status_text = "Unknown"
            
            # Capacity info
            capacity = event.get('capacity')
            registered = event.get('registered_count', 0)
            capacity_str = f"({registered}/{capacity})" if capacity else f"({registered} registered)"
            
            with st.expander(f"{status_icon} {event.get('name', 'Unknown')} - {start_str} {capacity_str}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write("**Event Details**")
                    st.write(f"**Name:** {event.get('name', 'N/A')}")
                    st.write(f"**Event ID:** {event.get('event_id', 'N/A')}")
                    st.write(f"**Type:** {event.get('event_type', 'N/A')}")
                    st.write(f"**Status:** {status_text}")
                    if event.get('sponsor_tier'):
                        st.write(f"**Sponsor:** {event.get('sponsor_tier')} Tier")
                
                with col2:
                    st.write("**Schedule & Location**")
                    st.write(f"**Start:** {start_str}")
                    st.write(f"**End:** {end_str}")
                    st.write(f"**Location:** {event.get('location', 'N/A')}")
                    st.write(f"**Capacity:** {capacity if capacity else 'Unlimited'}")
                    st.write(f"**Registered:** {registered}")
                    st.write(f"**Registration Required:** {'Yes' if event.get('registration_required') else 'No'}")
                
                with col3:
                    st.write("**Actions**")
                    edit_key = f"edit_event_{event.get('_id', idx)}"
                    delete_key = f"delete_event_{event.get('_id', idx)}"
                    
                    if st.button("✏️ Edit", key=edit_key, use_container_width=True):
                        st.session_state[f"editing_event_{event['_id']}"] = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=delete_key, type="secondary", use_container_width=True):
                        st.session_state[f"confirm_delete_event_{event['_id']}"] = True
                        st.rerun()
                
                # Description
                if event.get("description"):
                    st.divider()
                    st.markdown("**📝 Description:**")
                    st.write(event["description"])
                
                # Edit form (inline)
                if st.session_state.get(f"editing_event_{event['_id']}", False):
                    st.divider()
                    st.subheader("Edit Event")
                    
                    with st.form(f"edit_form_event_{event['_id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_title = st.text_input("Event Title", value=event.get('name', ''))
                            edit_type = st.selectbox("Event Type", [
                                "Career Fair", "Networking", "Workshop", "Conference", 
                                "Seminar", "Social Event", "Other"
                            ], index=["Career Fair", "Networking", "Workshop", "Conference", 
                                     "Seminar", "Social Event", "Other"].index(event.get('event_type', 'Other')))
                            edit_location = st.text_input("Location", value=event.get('location', ''))
                        
                        with col2:
                            # Parse existing dates
                            try:
                                existing_start = datetime.fromisoformat(event.get('start_datetime', ''))
                                existing_end = datetime.fromisoformat(event.get('end_datetime', ''))
                            except:
                                from datetime import datetime, timezone
                                existing_start = datetime.now(timezone.utc)
                                existing_end = datetime.now(timezone.utc)
                            
                            edit_start_date = st.date_input("Start Date", value=existing_start.date())
                            edit_start_time = st.time_input("Start Time", value=existing_start.time())
                            edit_end_date = st.date_input("End Date", value=existing_end.date())
                            edit_end_time = st.time_input("End Time", value=existing_end.time())
                        
                        edit_description = st.text_area("Description", value=event.get('description', ''))
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            edit_capacity = st.number_input("Capacity", min_value=0, value=event.get('capacity', 0) or 0)
                        with col2:
                            edit_registration = st.checkbox("Registration Required", value=event.get('registration_required', True))
                        with col3:
                            sponsor_options = ["None", "Bronze", "Silver", "Gold", "Platinum"]
                            current_sponsor = event.get('sponsor_tier', 'None')
                            if current_sponsor not in sponsor_options:
                                current_sponsor = "None"
                            edit_sponsor = st.selectbox("Sponsor Tier", sponsor_options, 
                                                       index=sponsor_options.index(current_sponsor))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                from datetime import datetime, timezone
                                new_start = datetime.combine(edit_start_date, edit_start_time).replace(tzinfo=timezone.utc)
                                new_end = datetime.combine(edit_end_date, edit_end_time).replace(tzinfo=timezone.utc)
                                
                                if new_end <= new_start:
                                    st.error("End date/time must be after start date/time")
                                else:
                                    updates = {
                                        "name": edit_title,
                                        "event_type": edit_type,
                                        "description": edit_description if edit_description else None,
                                        "start_datetime": new_start,
                                        "end_datetime": new_end,
                                        "location": edit_location,
                                        "capacity": edit_capacity if edit_capacity > 0 else None,
                                        "registration_required": edit_registration,
                                        "sponsor_tier": edit_sponsor if edit_sponsor != "None" else None
                                    }
                                    
                                    result = event_service.update_event(event['_id'], updates)
                                    
                                    if "error" in result:
                                        st.error(f"Error updating event: {result['error']}")
                                    else:
                                        st.success("✅ Event updated successfully!")
                                        del st.session_state[f"editing_event_{event['_id']}"]
                                        st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                del st.session_state[f"editing_event_{event['_id']}"]
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_event_{event['_id']}", False):
                    st.divider()
                    st.warning(f"⚠️ Are you sure you want to delete **{event.get('name', 'this event')}**? This action cannot be undone.")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_yes_event_{event['_id']}", type="primary"):
                            result = event_service.delete_event(event['_id'])
                            
                            if "error" in result:
                                st.error(f"Error deleting event: {result['error']}")
                            else:
                                st.success(f"✅ Event '{event.get('name', 'Unknown')}' deleted successfully!")
                                del st.session_state[f"confirm_delete_event_{event['_id']}"]
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"confirm_no_event_{event['_id']}"):
                            del st.session_state[f"confirm_delete_event_{event['_id']}"]
                            st.rerun()



def render_case_competitions_page():
    """Render the case competitions page with full CRUD"""
    st.title("🏆 Case Competitions")
    
    # Initialize services
    case_comp_service = CaseCompService()
    event_service = EventService()
    
    # Add New Competition Section (at top)
    with st.expander("➕ Create New Competition", expanded=False):
        with st.form("create_competition_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                comp_name = st.text_input("Competition Name *", placeholder="Finance Case Challenge 2025")
                competition_id = st.text_input("Competition ID *", placeholder="COMP001")
                
                # Get all events for dropdown
                all_events = event_service.list_events()
                if all_events:
                    event_options = {f"{e.get('name', 'Unknown')} ({e.get('event_id', 'N/A')})": e.get('event_id') for e in all_events}
                    selected_event_display = st.selectbox("Related Event *", options=list(event_options.keys()))
                    selected_event_id = event_options[selected_event_display]
                else:
                    st.warning("⚠️ No events found. Please create an event first.")
                    selected_event_id = st.text_input("Event ID *", placeholder="EVT001")
            
            with col2:
                min_team_size = st.number_input("Minimum Team Size *", min_value=1, max_value=10, value=2)
                max_team_size = st.number_input("Maximum Team Size *", min_value=1, max_value=10, value=5)
                prizes = st.text_input("Prizes (optional)", placeholder="1st: $5000, 2nd: $3000, 3rd: $1000")
            
            # Judges field - comma-separated
            judges_input = st.text_input("Judges (comma-separated) *", placeholder="Dr. Smith, Prof. Johnson, Ms. Lee")
            
            description = st.text_area("Description", placeholder="Competition details, rules, and requirements...")
            
            submitted = st.form_submit_button("Create Competition", type="primary")
            
            if submitted:
                if not all([comp_name, competition_id, selected_event_id, judges_input]):
                    st.error("Please fill in all required fields marked with *")
                elif max_team_size < min_team_size:
                    st.error("Maximum team size must be greater than or equal to minimum team size")
                else:
                    # Parse judges
                    judges = [j.strip() for j in judges_input.split(",") if j.strip()]
                    
                    if not judges:
                        st.error("Please provide at least one judge")
                    else:
                        # Create competition data
                        comp_data = {
                            "competition_id": competition_id,
                            "name": comp_name,
                            "event_id": selected_event_id,
                            "description": description if description else "",
                            "judges": judges,
                            "min_team_size": min_team_size,
                            "max_team_size": max_team_size,
                            "prizes": prizes if prizes else None
                        }
                        
                        # Create competition
                        result = case_comp_service.create_case_competition(comp_data)
                        
                        if "error" in result:
                            st.error(f"Error creating competition: {result['error']}")
                        else:
                            st.success(f"✅ Competition '{comp_name}' created successfully!")
                            st.rerun()
    
    st.divider()
    
    # Search and Filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search competitions", placeholder="Search by name or competition ID...")
    with col2:
        st.write("")  # Spacing
    with col3:
        if st.button("🔄 Refresh", use_container_width=True, key="refresh_comps"):
            st.rerun()
    
    # Get all competitions
    competitions = case_comp_service.list_case_competitions()
    
    if not competitions:
        st.info("📭 No competitions created yet. Create your first competition above!")
    else:
        # Client-side filtering by search
        if search_query:
            filtered_comps = [
                c for c in competitions
                if search_query.lower() in c.get("name", "").lower()
                or search_query.lower() in c.get("competition_id", "").lower()
            ]
        else:
            filtered_comps = competitions
        
        st.write(f"**Total Competitions:** {len(filtered_comps)} {f'(filtered from {len(competitions)})' if search_query else ''}")
        
        # Display competitions in expandable cards
        for idx, comp in enumerate(filtered_comps):
            # Get related event info
            event_info = "N/A"
            if comp.get('event_id'):
                event = event_service.get_event_by_id(comp['event_id'])
                if event and not isinstance(event, dict) or (isinstance(event, dict) and 'error' not in event):
                    event_info = f"{event.get('name', 'Unknown')} ({event.get('event_id', 'N/A')})"
            
            with st.expander(f"🏆 {comp.get('name', 'Unknown')} - {comp.get('competition_id', 'N/A')}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write("**Competition Details**")
                    st.write(f"**Name:** {comp.get('name', 'N/A')}")
                    st.write(f"**Competition ID:** {comp.get('competition_id', 'N/A')}")
                    st.write(f"**Related Event:** {event_info}")
                    if comp.get('prizes'):
                        st.write(f"**Prizes:** {comp.get('prizes')}")
                
                with col2:
                    st.write("**Team & Judging**")
                    st.write(f"**Team Size:** {comp.get('min_team_size', 'N/A')} - {comp.get('max_team_size', 'N/A')} members")
                    judges = comp.get('judges', [])
                    st.write(f"**Judges ({len(judges)}):** {', '.join(judges) if judges else 'None'}")
                
                with col3:
                    st.write("**Actions**")
                    edit_key = f"edit_comp_{comp.get('_id', idx)}"
                    delete_key = f"delete_comp_{comp.get('_id', idx)}"
                    
                    if st.button("✏️ Edit", key=edit_key, use_container_width=True):
                        st.session_state[f"editing_comp_{comp['_id']}"] = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=delete_key, type="secondary", use_container_width=True):
                        st.session_state[f"confirm_delete_comp_{comp['_id']}"] = True
                        st.rerun()
                
                # Description
                if comp.get("description"):
                    st.divider()
                    st.markdown("**📝 Description:**")
                    st.write(comp["description"])
                
                # Edit form (inline)
                if st.session_state.get(f"editing_comp_{comp['_id']}", False):
                    st.divider()
                    st.subheader("Edit Competition")
                    
                    with st.form(f"edit_form_comp_{comp['_id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Competition Name", value=comp.get('name', ''))
                            
                            # Event dropdown for editing
                            all_events = event_service.list_events()
                            if all_events:
                                event_options = {f"{e.get('name', 'Unknown')} ({e.get('event_id', 'N/A')})": e.get('event_id') for e in all_events}
                                # Find current event
                                current_event_id = comp.get('event_id', '')
                                current_event_display = None
                                for display, eid in event_options.items():
                                    if eid == current_event_id:
                                        current_event_display = display
                                        break
                                
                                if current_event_display:
                                    current_index = list(event_options.keys()).index(current_event_display)
                                else:
                                    current_index = 0
                                
                                selected_event_display = st.selectbox("Related Event", options=list(event_options.keys()), index=current_index)
                                edit_event_id = event_options[selected_event_display]
                            else:
                                edit_event_id = st.text_input("Event ID", value=comp.get('event_id', ''))
                            
                            edit_min_team = st.number_input("Minimum Team Size", min_value=1, max_value=10, value=comp.get('min_team_size', 2))
                        
                        with col2:
                            edit_max_team = st.number_input("Maximum Team Size", min_value=1, max_value=10, value=comp.get('max_team_size', 5))
                            edit_prizes = st.text_input("Prizes", value=comp.get('prizes', ''))
                            edit_judges = st.text_input("Judges (comma-separated)", value=", ".join(comp.get('judges', [])))
                        
                        edit_description = st.text_area("Description", value=comp.get('description', ''))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                if edit_max_team < edit_min_team:
                                    st.error("Maximum team size must be >= minimum team size")
                                else:
                                    # Parse judges
                                    new_judges = [j.strip() for j in edit_judges.split(",") if j.strip()]
                                    
                                    updates = {
                                        "name": edit_name,
                                        "event_id": edit_event_id,
                                        "description": edit_description if edit_description else "",
                                        "judges": new_judges,
                                        "min_team_size": edit_min_team,
                                        "max_team_size": edit_max_team,
                                        "prizes": edit_prizes if edit_prizes else None
                                    }
                                    
                                    result = case_comp_service.update_case_competition(comp['_id'], updates)
                                    
                                    if "error" in result:
                                        st.error(f"Error updating competition: {result['error']}")
                                    else:
                                        st.success("✅ Competition updated successfully!")
                                        del st.session_state[f"editing_comp_{comp['_id']}"]
                                        st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                del st.session_state[f"editing_comp_{comp['_id']}"]
                                st.rerun()
                
                # Delete confirmation
                if st.session_state.get(f"confirm_delete_comp_{comp['_id']}", False):
                    st.divider()
                    st.warning(f"⚠️ Are you sure you want to delete **{comp.get('name', 'this competition')}**? This action cannot be undone.")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_yes_comp_{comp['_id']}", type="primary"):
                            result = case_comp_service.delete_case_competition(comp['_id'])
                            
                            if "error" in result:
                                st.error(f"Error deleting competition: {result['error']}")
                            else:
                                st.success(f"✅ Competition '{comp.get('name', 'Unknown')}' deleted successfully!")
                                del st.session_state[f"confirm_delete_comp_{comp['_id']}"]
                                st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"confirm_no_comp_{comp['_id']}"):
                            del st.session_state[f"confirm_delete_comp_{comp['_id']}"]
                            st.rerun()



def render_matching_page():
    """Render the AI matching page"""
    from ai.workflow import WorkflowEngine
    
    st.title("🤖 Mentor Matching (AI)")
    st.markdown("*AI-powered student-mentor matching with automated email outreach*")
    st.divider()
    
    # Initialize services
    student_service = StudentService()
    match_service = MatchService()
    email_service = EmailService()
    workflow = WorkflowEngine()
    
    # Get all students
    students = student_service.list_students()
    
    if not students:
        st.warning("⚠️ No students found. Please add students first.")
        return
    
    # Create student options
    student_options = {f"{s.get('name')} ({s.get('student_id')})": s.get('student_id') 
                      for s in students}
    
    # Layout: Input Section
    st.subheader("🎯 Run Matching Workflow")
    
    col1, col2, col3 = st.columns([3, 1, 2])
    
    with col1:
        selected_student = st.selectbox(
            "Select Student",
            options=list(student_options.keys()),
            help="Choose a student to match with mentors"
        )
        student_id = student_options[selected_student]
    
    with col2:
        top_n = st.number_input(
            "Top Matches",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of top mentors to match"
        )
    
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        run_button = st.button(
            "🚀 Run AI Matching Workflow",
            type="primary",
            use_container_width=True
        )
    
    st.divider()
    
    # Run workflow when button clicked
    if run_button:
        with st.spinner("🔄 Running AI matching workflow..."):
            result = workflow.run_matching_workflow_for_student(
                student_id=student_id,
                top_n=top_n
            )
        
        # Display results
        if result['success']:
            st.success(f"✅ Successfully created {result['matches_created']} matches and scheduled {result['emails_scheduled']} emails!")
            
            # Display new matches
            st.subheader("📊 New Match Results")
            
            for i, match in enumerate(result['match_details'], 1):
                if match.get('error'):
                    with st.expander(f"❌ Match {i}: {match['mentor_name']} (Error)", expanded=False):
                        st.error(match['error'])
                else:
                    # Get email details for this match
                    email_log = None
                    if match.get('email_id'):
                        email_log = email_service.get_email_log_by_id(match['email_id'])
                    
                    with st.expander(f"✅ Match {i}: {match['mentor_name']} - {match['score']:.1%} Match", expanded=(i==1)):
                        col_a, col_b = st.columns([2, 1])
                        
                        with col_a:
                            st.markdown(f"**Mentor:** {match['mentor_name']}")
                            st.markdown(f"**Email:** {match['mentor_email']}")
                            st.markdown(f"**Match Score:** {match['score']:.1%}")
                            st.markdown(f"**Rank:** #{match['rank']}")
                        
                        with col_b:
                            if email_log:
                                st.markdown(f"**📧 Email Status:** `{email_log.get('status')}`")
                                send_time = email_log.get('planned_send_time')
                                if send_time:
                                    st.markdown(f"**⏰ Scheduled For:**")
                                    st.info(send_time)
                            
                            st.markdown(f"**🔗 Match ID:**")
                            st.code(match['match_id'], language=None)
                        
                        # Show AI-generated match reason
                        if email_log and email_log.get('body'):
                            st.markdown("**🤖 AI-Generated Email:**")
                            st.markdown(f"**Subject:** {email_log.get('subject')}")
                            with st.container():
                                st.text_area(
                                    "Email Body",
                                    value=email_log.get('body'),
                                    height=200,
                                    disabled=True,
                                    key=f"email_body_{i}"
                                )
        else:
            st.error("❌ Workflow failed")
            for error in result['errors']:
                st.warning(f"⚠️ {error}")
    
    # Show past matches for selected student
    st.divider()
    st.subheader("📚 Past Matches for Selected Student")
    
    # Get past matches
    past_matches = match_service.list_matches({"student_id": student_id})
    
    if past_matches:
        # Convert to DataFrame for better display
        match_data = []
        for match in past_matches:
            # Get mentor details
            mentor_service = MentorService()
            mentor = mentor_service.get_mentor_by_id(match.get('mentor_id'))
            mentor_name = mentor.get('name', 'Unknown') if mentor else 'Unknown'
            
            match_data.append({
                "Match ID": match.get('_id', 'N/A')[:12] + "...",
                "Mentor": mentor_name,
                "Score": f"{match.get('match_score', 0):.1%}",
                "Status": match.get('status', 'unknown'),
                "Reason": match.get('reason_summary', 'N/A')[:80] + "..." if len(match.get('reason_summary', '')) > 80 else match.get('reason_summary', 'N/A')
            })
        
        df = pd.DataFrame(match_data)
        
        # Display as table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Match ID": st.column_config.TextColumn("Match ID", width="small"),
                "Mentor": st.column_config.TextColumn("Mentor", width="medium"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Reason": st.column_config.TextColumn("AI Match Reason", width="large")
            }
        )
        
        st.caption(f"📊 Total matches: {len(past_matches)}")
    else:
        st.info("No past matches found for this student.")


def render_email_management_page():
    """Render the email management page"""
    st.title("📧 Email Management")
    
    tab1, tab2, tab3 = st.tabs(["Send Email", "Templates", "History"])
    
    with tab1:
        st.subheader("Send Email via N8N")
        
        recipients = st.multiselect("Recipients", ["Students", "Mentors", "All"])
        subject = st.text_input("Subject")
        message = st.text_area("Message", height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate with AI", type="secondary"):
                st.info("AI email generation coming soon!")
        with col2:
            if st.button("Send Email", type="primary"):
                st.info("Email sending functionality coming soon!")
    
    with tab2:
        st.subheader("Email Templates")
        st.info("No templates created yet")
    
    with tab3:
        st.subheader("Email History")
        st.info("No emails sent yet")


def main():
    """Main application entry point"""
    # Initialize the app
    init_app()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render the selected page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Students":
        render_students_page()
    elif page == "Mentors":
        render_mentors_page()
    elif page == "Events":
        render_events_page()
    elif page == "Case Competitions":
        render_case_competitions_page()
    elif page == "Matching":
        render_matching_page()
    elif page == "Email Management":
        render_email_management_page()


if __name__ == "__main__":
    main()
