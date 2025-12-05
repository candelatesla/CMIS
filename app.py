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
from utils.auth import check_login


def init_app():
    """Initialize the application"""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply TAMU Aggie Theme
    apply_tamu_theme()
    
    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
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


def apply_tamu_theme():
    """Apply Texas A&M Aggie Maroon theme to the dashboard"""
    st.markdown("""
    <style>
        /* Sidebar - Aggie Maroon background with white text */
        [data-testid="stSidebar"] {
            background-color: #500000 !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        
        /* Main panel - White background with black text */
        .main,
        [data-testid="stAppViewContainer"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        
        /* Main panel titles and headers - Black */
        .main h1,
        .main h2,
        .main h3,
        .main h4,
        .main h5,
        .main h6,
        .main p{
            color: #000000 !important;
        }
        
        /* Card-style background for main content */
        .main .block-container {
            background-color: #F8F9FA !important;
            border-radius: 15px !important;
            padding: 2rem !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Card style for expanders and forms */
        .stExpander,
        [data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            border: 1px solid #E0E0E0 !important;
            padding: 0.5rem !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05) !important;
        }
        
        /* Form containers */
        [data-testid="stForm"] {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            padding: 1.5rem !important;
            border: 1px solid #E0E0E0 !important;
        }
        
        /* Metric cards */
        [data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            padding: 1rem !important;
            border: 1px solid #E0E0E0 !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05) !important;
        }
        
        /* Text-only buttons (no background) */
        button[kind="secondary"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #500000 !important;
            padding: 0.25rem 0.5rem !important;
        }
        
        button[kind="secondary"]:hover {
            background-color: rgba(80, 0, 0, 0.05) !important;
            color: #500000 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_login_page():
    """Render the streamlined smart login page with auto-onboarding"""
    from services.auth_service import AuthService
    from services.student_service import StudentService
    from services.mentor_service import MentorService
    
    # Hide sidebar on login page
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize services
    auth_service = AuthService()
    student_service = StudentService()
    mentor_service = MentorService()
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🎓 CMIS Platform")
        st.markdown("### Login to your account")
        st.markdown("---")
        
        # Check if we're in registration mode
        if "registration_mode" not in st.session_state:
            st.session_state["registration_mode"] = None
        
        # Registration mode routing
        if st.session_state["registration_mode"] == "student":
            render_student_registration()
            return
        elif st.session_state["registration_mode"] == "mentor":
            render_mentor_registration()
            return
        
        # Login form
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@tamu.edu")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if not email or not password:
                    st.error("❌ Please enter both email and password.")
                else:
                    # Check if admin first (existing behavior - DO NOT BREAK)
                    if check_login(email, password):
                        st.session_state["authenticated"] = True
                        st.session_state["role"] = "admin"
                        st.session_state["admin_email"] = email
                        st.session_state["email"] = email
                        st.success("✅ Admin login successful!")
                        st.rerun()
                        return
                    
                    # Try auth_users lookup for student
                    user = auth_service.authenticate_user(email, password, "student")
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["role"] = "student"
                        st.session_state["email"] = email
                        st.session_state["linked_student_id"] = user.get("linked_student_id")
                        st.success("✅ Student login successful!")
                        st.rerun()
                        return
                    
                    # Try auth_users lookup for mentor
                    user = auth_service.authenticate_user(email, password, "mentor")
                    if user:
                        st.session_state["authenticated"] = True
                        st.session_state["role"] = "mentor"
                        st.session_state["email"] = email
                        st.session_state["linked_mentor_id"] = user.get("linked_mentor_id")
                        st.success("✅ Mentor login successful!")
                        st.rerun()
                        return
                    
                    # AUTO-ONBOARDING: Check if user exists in students collection
                    students = student_service.list_students()
                    student_match = None
                    for student in students:
                        if student.get("email", "").lower() == email.lower():
                            student_match = student
                            break
                    
                    if student_match:
                        # Create auth_users entry with default password
                        auth_result = auth_service.create_user(
                            email=email,
                            password="Passw0rd!",
                            role="student",
                            linked_student_id=student_match.get("student_id")
                        )
                        
                        if "error" not in auth_result:
                            # Now verify the password they entered
                            if auth_service.verify_password(password, auth_service.hash_password("Passw0rd!")):
                                st.session_state["authenticated"] = True
                                st.session_state["role"] = "student"
                                st.session_state["email"] = email
                                st.session_state["linked_student_id"] = student_match.get("student_id")
                                st.success("✅ Account created and logged in! (Default password: Passw0rd!)")
                                st.rerun()
                                return
                            else:
                                st.error("❌ Account found. Default password is: Passw0rd!")
                                return
                    
                    # AUTO-ONBOARDING: Check if user exists in mentors collection
                    mentors = mentor_service.list_mentors()
                    mentor_match = None
                    for mentor in mentors:
                        if mentor.get("email", "").lower() == email.lower():
                            mentor_match = mentor
                            break
                    
                    if mentor_match:
                        # Create auth_users entry with default password
                        auth_result = auth_service.create_user(
                            email=email,
                            password="Passw0rd!",
                            role="mentor",
                            linked_mentor_id=mentor_match.get("mentor_id")
                        )
                        
                        if "error" not in auth_result:
                            # Now verify the password they entered
                            if auth_service.verify_password(password, auth_service.hash_password("Passw0rd!")):
                                st.session_state["authenticated"] = True
                                st.session_state["role"] = "mentor"
                                st.session_state["email"] = email
                                st.session_state["linked_mentor_id"] = mentor_match.get("mentor_id")
                                st.success("✅ Account created and logged in! (Default password: Passw0rd!)")
                                st.rerun()
                                return
                            else:
                                st.error("❌ Account found. Default password is: Passw0rd!")
                                return
                    
                    # If we get here, no account found anywhere
                    st.error("❌ No account found for this email. Please register as a student or mentor.")
        
        st.markdown("---")
        st.markdown("### Don't have an account?")
        st.markdown("**Register as:**")
        
        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            if st.button("🎓 Student", use_container_width=True):
                st.session_state["registration_mode"] = "student"
                st.rerun()
        
        with col_reg2:
            if st.button("🧑‍🏫 Mentor/Judge", use_container_width=True):
                st.session_state["registration_mode"] = "mentor"
                st.rerun()
        
        st.markdown("---")
        st.caption("CMIS Engagement Platform")


def render_student_registration():
    """Render student registration form"""
    from services.auth_service import AuthService
    from services.student_service import StudentService
    from utils.pdf_utils import extract_text_from_pdf
    
    auth_service = AuthService()
    student_service = StudentService()
    
    st.markdown("### 🎓 Student Registration")
    st.markdown("Create your student account")
    st.markdown("---")
    
    with st.form("student_registration_form"):
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Smith")
            email = st.text_input("TAMU Email *", placeholder="student@tamu.edu")
            student_id = st.text_input("Student ID / UIN *", placeholder="123456789")
        
        with col2:
            password = st.text_input("Password *", type="password", placeholder="Min 6 characters")
            password_confirm = st.text_input("Confirm Password *", type="password")
        
        st.subheader("Academic Information")
        col3, col4 = st.columns(2)
        
        with col3:
            major = st.selectbox("Major *", [
                "Computer Science", "Information Systems", "Data Science",
                "Engineering", "Business", "Finance", "Accounting",
                "Management Information Systems", "Statistics", "Mathematics", "Other"
            ])
        
        with col4:
            grad_year = st.selectbox("Graduation Year *", [2025, 2026, 2027, 2028, 2029, 2030])
        
        skills = st.multiselect("Skills *", [
            "Python", "Java", "C++", "JavaScript", "React", "SQL",
            "Machine Learning", "Data Analysis", "Web Development",
            "Cloud Computing", "Project Management", "Communication",
            "Leadership", "Problem Solving", "Teamwork"
        ])
        
        interests = st.multiselect("Interests *", [
            "Software Development", "Data Science", "AI/ML", "Cybersecurity",
            "Consulting", "Finance", "Entrepreneurship", "Research",
            "Product Management", "Business Analytics"
        ])
        
        st.subheader("Resume")
        uploaded_resume = st.file_uploader("Upload Resume (PDF) *", type=["pdf"])
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        with col_btn2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if cancel:
            st.session_state["registration_mode"] = None
            st.rerun()
        
        if submit:
            # Validation
            if not all([name, email, student_id, password, password_confirm, major, uploaded_resume]):
                st.error("❌ Please fill in all required fields.")
            elif not email.endswith("@tamu.edu"):
                st.error("❌ Please use your TAMU email (@tamu.edu)")
            elif password != password_confirm:
                st.error("❌ Passwords do not match.")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters.")
            elif not skills or not interests:
                st.error("❌ Please select at least one skill and one interest.")
            else:
                # Check if user exists
                existing = auth_service.get_user(email, "student")
                if existing:
                    st.error("❌ An account with this email already exists.")
                else:
                    # Parse resume
                    try:
                        resume_text = extract_text_from_pdf(uploaded_resume)
                    except Exception as e:
                        st.error(f"❌ Error parsing resume: {str(e)}")
                        resume_text = ""
                    
                    if resume_text:
                        # Create student record
                        student_data = {
                            "name": name,
                            "email": email,
                            "student_id": student_id,
                            "major": major,
                            "grad_year": grad_year,
                            "gpa": 3.5,  # Default
                            "interests": interests,
                            "skills": skills,
                            "resume_text": resume_text
                        }
                        
                        student_result = student_service.create_student(student_data)
                        
                        if "error" in student_result:
                            st.error(f"❌ Error: {student_result['error']}")
                        else:
                            # Create auth user
                            auth_result = auth_service.create_user(
                                email=email,
                                password=password,
                                role="student",
                                linked_student_id=student_result.get("student_id")
                            )
                            
                            if "error" in auth_result:
                                st.error(f"❌ Error: {auth_result['error']}")
                            else:
                                st.success("✅ Registration successful! Please log in.")
                                st.balloons()
                                st.session_state["registration_mode"] = None
                                # Force rerun after short delay
                                import time
                                time.sleep(2)
                                st.rerun()


def render_mentor_registration():
    """Render mentor/judge registration form"""
    from services.auth_service import AuthService
    from services.mentor_service import MentorService
    from utils.pdf_utils import extract_text_from_pdf
    
    auth_service = AuthService()
    mentor_service = MentorService()
    
    st.markdown("### 🧑‍🏫 Mentor/Judge Registration")
    st.markdown("Create your mentor account")
    st.markdown("---")
    
    with st.form("mentor_registration_form"):
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Sarah Johnson")
            email = st.text_input("Email *", placeholder="mentor@company.com")
            company = st.text_input("Company *", placeholder="Tech Corp")
        
        with col2:
            password = st.text_input("Password *", type="password", placeholder="Min 6 characters")
            password_confirm = st.text_input("Confirm Password *", type="password")
            job_title = st.text_input("Job Title *", placeholder="Senior Engineer")
        
        st.subheader("Professional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            industry = st.selectbox("Industry *", [
                "Technology", "Finance", "Consulting", "Healthcare",
                "Education", "Manufacturing", "Retail", "Energy", "Other"
            ])
        
        with col4:
            years_experience = st.number_input("Years of Experience *", min_value=0, max_value=50, value=5)
        
        expertise = st.multiselect("Expertise Areas *", [
            "Software Development", "Data Science", "Cloud Computing",
            "Project Management", "Business Strategy", "Finance",
            "Marketing", "Operations", "Leadership", "Consulting",
            "Product Management", "Engineering"
        ])
        
        interests = st.multiselect("Mentoring Interests", [
            "Career Development", "Technical Skills", "Leadership",
            "Professional Networking", "Industry Insights", "Entrepreneurship"
        ])
        
        st.subheader("Resume/Bio")
        uploaded_resume = st.file_uploader("Upload Resume/Bio (PDF) *", type=["pdf"])
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        with col_btn2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if cancel:
            st.session_state["registration_mode"] = None
            st.rerun()
        
        if submit:
            # Validation
            if not all([name, email, company, job_title, industry, password, password_confirm, uploaded_resume]):
                st.error("❌ Please fill in all required fields.")
            elif password != password_confirm:
                st.error("❌ Passwords do not match.")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters.")
            elif not expertise:
                st.error("❌ Please select at least one expertise area.")
            else:
                # Check if user exists
                existing = auth_service.get_user(email, "mentor")
                if existing:
                    st.error("❌ An account with this email already exists.")
                else:
                    # Parse resume
                    try:
                        resume_text = extract_text_from_pdf(uploaded_resume)
                    except Exception as e:
                        st.error(f"❌ Error parsing resume: {str(e)}")
                        resume_text = ""
                    
                    if resume_text:
                        # Generate unique mentor ID
                        import random
                        mentor_id = f"MEN{random.randint(10000, 99999)}"
                        
                        # Create mentor record
                        mentor_data = {
                            "name": name,
                            "email": email,
                            "mentor_id": mentor_id,
                            "company": company,
                            "job_title": job_title,
                            "industry": industry,
                            "years_experience": years_experience,
                            "expertise_areas": expertise,
                            "interests": interests if interests else [],
                            "max_mentees": 3,
                            "current_mentees": 0,
                            "resume_text": resume_text
                        }
                        
                        mentor_result = mentor_service.create_mentor(mentor_data)
                        
                        if "error" in mentor_result:
                            st.error(f"❌ Error: {mentor_result['error']}")
                        else:
                            # Create auth user
                            auth_result = auth_service.create_user(
                                email=email,
                                password=password,
                                role="mentor",
                                linked_mentor_id=mentor_result.get("mentor_id")
                            )
                            
                            if "error" in auth_result:
                                st.error(f"❌ Error: {auth_result['error']}")
                            else:
                                st.success("✅ Registration successful! Please log in.")
                                st.balloons()
                                st.session_state["registration_mode"] = None
                                # Force rerun after short delay
                                import time
                                time.sleep(2)
                                st.rerun()


def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.title("🎓 CMIS Dashboard")

        st.divider()
        
        page = st.radio(
             "Navigation",
            [
                "🗂️ Dashboard",
                "🎓 Students",
                "🧑‍🏫 Mentors",
                "📅 Events",
                "🏆 Case Competitions",
                "🤖 Matching",
                "👥 Mentorship Tracker",
                "📨 Email Management"
            ]
        )
        
        st.divider()
        st.caption("Admin Tools")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state.pop("admin_email", None)
            st.rerun()
        
        # Show logged in user
        if "admin_email" in st.session_state:
            st.caption(f"Logged in as: {st.session_state['admin_email']}")
        
        return page


def render_dashboard():
    """Render the main dashboard page"""
    st.title("Dashboard Overview")
    
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
    
    # Bulk Upload Section
    with st.expander("📤 Bulk Upload Students (CSV)", expanded=False):
        st.markdown("""
        Upload a CSV file to add multiple students at once.
        
        **Required CSV columns:**
        - `student_id`, `name`, `email`, `major`, `grad_year`, `interests`, `skills`, `resume_text`
        
        **Notes:**
        - `interests` and `skills` should be comma-separated values (e.g., "AI, Web Dev, Data Science")
        - `resume_text` can be empty (will use sample resume)
        - Students with existing emails will be skipped
        """)
        
        uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"], key="bulk_students_csv")
        
        if uploaded_csv is not None:
            try:
                # Parse CSV
                df = pd.read_csv(uploaded_csv)
                
                st.write(f"**Found {len(df)} rows in CSV**")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("🚀 Process CSV and Import Students", type="primary"):
                    results = {
                        "inserted": 0,
                        "skipped": 0,
                        "errors": []
                    }
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, row in df.iterrows():
                        status_text.text(f"Processing row {idx + 1}/{len(df)}...")
                        progress_bar.progress((idx + 1) / len(df))
                        
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
                                # Use sample resume
                                try:
                                    resume_text = get_random_student_resume()
                                except:
                                    resume_text = ""
                            
                            # Validate required fields
                            if not all([student_id, name, email, major]):
                                results["errors"].append(f"Row {idx + 1}: Missing required fields")
                                continue
                            
                            # Check if student already exists by email
                            existing = student_service.get_student_by_email(email)
                            if existing:
                                results["skipped"] += 1
                                continue
                            
                            # Create student data
                            student_data = {
                                "student_id": student_id,
                                "name": name,
                                "email": email,
                                "major": major,
                                "grad_year": grad_year,
                                "gpa": float(row.get('gpa', 3.5)) if 'gpa' in row else 3.5,
                                "interests": interests,
                                "skills": skills,
                                "resume_text": resume_text
                            }
                            
                            # Create student
                            result = student_service.create_student(student_data)
                            
                            if "error" in result:
                                results["errors"].append(f"Row {idx + 1} ({name}): {result['error']}")
                            else:
                                results["inserted"] += 1
                        
                        except Exception as e:
                            results["errors"].append(f"Row {idx + 1}: {str(e)}")
                    
                    # Show results
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"✅ Import complete!")
                    st.write(f"**📊 Results:**")
                    st.write(f"- ✅ Inserted: {results['inserted']}")
                    st.write(f"- ⏭️ Skipped (already exists): {results['skipped']}")
                    st.write(f"- ❌ Errors: {len(results['errors'])}")
                    
                    if results['errors']:
                        with st.expander("View Errors"):
                            for error in results['errors']:
                                st.write(f"- {error}")
                    
                    if results['inserted'] > 0:
                        st.rerun()
            
            except Exception as e:
                st.error(f"Error parsing CSV: {str(e)}")
    
    st.divider()
    
    # Search and Filter
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search students", placeholder="Search by name, email, major, or student ID...")
    with col2:
        st.write("")  # Spacing
    with col3:
        if st.button("🔄 Refresh", type="secondary"):
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
    
    # Bulk Upload Section
    with st.expander("📤 Bulk Upload Mentors (CSV)", expanded=False):
        st.markdown("""
        Upload a CSV file to add multiple mentors at once.
        
        **Required CSV columns:**
        - `mentor_id`, `name`, `email`, `company`, `job_title`, `industry`, `expertise_areas`, `interests`, `max_mentees`
        
        **Notes:**
        - `expertise_areas` and `interests` should be comma-separated values (e.g., "Software Architecture, Cloud Computing")
        - `resume_text` can be empty (will use sample resume)
        - Mentors with existing emails will be skipped
        """)
        
        uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"], key="bulk_mentors_csv")
        
        if uploaded_csv is not None:
            try:
                # Parse CSV
                df = pd.read_csv(uploaded_csv)
                
                st.write(f"**Found {len(df)} rows in CSV**")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("🚀 Process CSV and Import Mentors", type="primary"):
                    results = {
                        "inserted": 0,
                        "skipped": 0,
                        "errors": []
                    }
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, row in df.iterrows():
                        status_text.text(f"Processing row {idx + 1}/{len(df)}...")
                        progress_bar.progress((idx + 1) / len(df))
                        
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
                                # Use sample resume
                                try:
                                    resume_text = get_random_mentor_resume()
                                except:
                                    resume_text = ""
                            
                            # Validate required fields
                            if not all([mentor_id, name, email, company, job_title, industry]):
                                results["errors"].append(f"Row {idx + 1}: Missing required fields")
                                continue
                            
                            # Check if mentor already exists by email
                            existing = mentor_service.get_mentor_by_email(email)
                            if existing:
                                results["skipped"] += 1
                                continue
                            
                            # Create mentor data
                            mentor_data = {
                                "mentor_id": mentor_id,
                                "name": name,
                                "email": email,
                                "company": company,
                                "job_title": job_title,
                                "industry": industry,
                                "years_experience": int(row.get('years_experience', 5)) if 'years_experience' in row else 5,
                                "expertise_areas": expertise_areas,
                                "interests": interests,
                                "max_mentees": max_mentees,
                                "current_mentees": 0,
                                "linkedin_url": str(row.get('linkedin_url', '')) if 'linkedin_url' in row and str(row.get('linkedin_url', '')) != 'nan' else None,
                                "resume_text": resume_text
                            }
                            
                            # Create mentor
                            result = mentor_service.create_mentor(mentor_data)
                            
                            if "error" in result:
                                results["errors"].append(f"Row {idx + 1} ({name}): {result['error']}")
                            else:
                                results["inserted"] += 1
                        
                        except Exception as e:
                            results["errors"].append(f"Row {idx + 1}: {str(e)}")
                    
                    # Show results
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success(f"✅ Import complete!")
                    st.write(f"**📊 Results:**")
                    st.write(f"- ✅ Inserted: {results['inserted']}")
                    st.write(f"- ⏭️ Skipped (already exists): {results['skipped']}")
                    st.write(f"- ❌ Errors: {len(results['errors'])}")
                    
                    if results['errors']:
                        with st.expander("View Errors"):
                            for error in results['errors']:
                                st.write(f"- {error}")
                    
                    if results['inserted'] > 0:
                        st.rerun()
            
            except Exception as e:
                st.error(f"Error parsing CSV: {str(e)}")
    
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
                
                # Teams registered for this event
                st.divider()
                st.markdown("**👥 Registered Teams:**")
                
                # Import team service
                from services.team_service import TeamService
                team_service = TeamService()
                
                # Get teams for this event
                event_id_str = str(event.get('_id', ''))
                teams = team_service.get_teams_by_event(event_id_str)
                
                if teams:
                    st.write(f"**{len(teams)} team(s) registered**")
                    st.markdown("")
                    
                    # Display each team with scoring details (no nested expanders)
                    for idx, team in enumerate(teams):
                        team_name = team.get('team_name', 'N/A')
                        members = team.get('members', [])
                        member_count = len(members)
                        member_names = ", ".join([m.get('name', 'Unknown') for m in members[:3]])
                        if member_count > 3:
                            member_names += f" + {member_count - 3} more"
                        
                        # Get scoring status
                        final_score = team.get('final_score')
                        judge_scores = team.get('judge_scores', {})
                        judges_assigned = team.get('judges_assigned', [])
                        
                        # Score display
                        if final_score is not None:
                            score_badge = f"✅ Scored: {final_score:.2f}/100"
                            status_color = "#d4edda"
                        elif judge_scores:
                            score_badge = f"⏳ Partially Scored: {len(judge_scores)}/{len(judges_assigned)} judges"
                            status_color = "#fff3cd"
                        else:
                            score_badge = "📝 Not Scored Yet"
                            status_color = "#f8f9fa"
                        
                        # Team card (no expander)
                        st.markdown(f"<div style='background-color: {status_color}; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)
                        st.markdown(f"**🏅 {team_name}** – {member_names}")
                        st.markdown(f"*{score_badge}*")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption(f"**Members ({member_count}):** " + ", ".join([m.get('name', 'Unknown') for m in members]))
                        
                        with col2:
                            st.caption(f"**Judges:** {len(judges_assigned)} assigned")
                            if final_score is not None:
                                st.caption(f"**Final Score:** {final_score:.2f}/100")
                        
                        # Show judge scores if available
                        if judge_scores:
                            st.markdown("**Judge Scores:**")
                            for judge_id, score_data in judge_scores.items():
                                score = score_data.get('score', 'N/A')
                                comments = score_data.get('comments', '')
                                st.caption(f"• Judge: {score}/100" + (f" – {comments}" if comments else ""))
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No teams registered yet")
                
                # Judge Assignment Section
                st.divider()
                st.markdown("**👨‍⚖️ Judges Assigned to This Event:**")
                
                # Get mentor service
                from services.mentor_service import MentorService
                mentor_service = MentorService()
                
                # Get all mentors for selection
                all_mentors = mentor_service.list_mentors()
                
                if all_mentors:
                    # Create mentor options dictionary
                    mentor_options = {}
                    for mentor in all_mentors:
                        display_name = f"{mentor.get('name', 'Unknown')} – {mentor.get('email', '')} – {mentor.get('company', 'N/A')}"
                        mentor_options[display_name] = str(mentor.get('_id'))
                    
                    # Get currently assigned judges
                    current_judges = event.get('judges_assigned', [])
                    
                    # Find default selections
                    default_selections = []
                    for display_name, mentor_id in mentor_options.items():
                        if mentor_id in current_judges:
                            default_selections.append(display_name)
                    
                    # Multiselect for judges
                    selected_judges_display = st.multiselect(
                        "Select judges for this event:",
                        options=list(mentor_options.keys()),
                        default=default_selections,
                        key=f"judges_select_{event['_id']}"
                    )
                    
                    # Convert display names to IDs
                    selected_judge_ids = [mentor_options[name] for name in selected_judges_display]
                    
                    col_save1, col_save2, col_save3 = st.columns([2, 1, 2])
                    with col_save2:
                        if st.button("💾 Save Judges", key=f"save_judges_{event['_id']}", use_container_width=True, type="primary"):
                            # Update event with judges
                            update_result = event_service.update_event(
                                event_id_str,
                                {"judges_assigned": selected_judge_ids}
                            )
                            
                            if "error" in update_result:
                                st.error(f"Error: {update_result['error']}")
                            else:
                                # Send email notifications to newly added judges
                                try:
                                    from services.email_service import EmailService
                                    email_service = EmailService()
                                    
                                    # Find newly added judges (not in current_judges)
                                    new_judge_ids = set(selected_judge_ids) - set(current_judges)
                                    
                                    if new_judge_ids:
                                        for judge_id in new_judge_ids:
                                            judge = mentor_service.get_mentor_by_id(judge_id)
                                            if judge:
                                                try:
                                                    email_service.send_judge_assignment_email(judge, event)
                                                except Exception as e:
                                                    print(f"Error sending email to judge {judge_id}: {str(e)}")
                                        
                                        st.toast(f"Judge updated & notified!", icon="✅")
                                    else:
                                        st.toast(f"Judges updated!", icon="✅")
                                except Exception as e:
                                    print(f"Error sending judge emails: {str(e)}")
                                    st.toast(f"Judges updated!", icon="✅")
                                
                                st.rerun()
                    
                    # Show current assignments
                    if current_judges:
                        st.write(f"**Currently assigned:** {len(current_judges)} judge(s)")
                    else:
                        st.info("No judges assigned yet")
                else:
                    st.warning("No mentors/judges available in the system")
                
                # Random Team Assignment Section
                if teams and current_judges:
                    st.divider()
                    st.markdown("**🎲 Random Team Assignment:**")
                    
                    col_rand1, col_rand2, col_rand3 = st.columns([2, 1, 2])
                    with col_rand2:
                        if st.button("🎲 Assign Teams Randomly", key=f"random_assign_{event['_id']}", use_container_width=True):
                            # Random distribution algorithm
                            import random
                            teams_copy = teams.copy()
                            random.shuffle(teams_copy)
                            
                            assignments = {}
                            for i, team in enumerate(teams_copy):
                                judge_id = current_judges[i % len(current_judges)]
                                assignments.setdefault(judge_id, []).append(team)
                            
                            # Update each team
                            success_count = 0
                            for judge_id, assigned_teams in assignments.items():
                                for team in assigned_teams:
                                    result = team_service.update_team(
                                        team['_id'],
                                        {"judges_assigned": [str(judge_id)]}  # Ensure string ID
                                    )
                                    if "error" not in result:
                                        success_count += 1
                            
                            if success_count > 0:
                                st.success(f"✅ Assigned {success_count} team(s) across {len(current_judges)} judge(s)")
                                st.balloons()
                                import time
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to assign teams")
                    
                    st.caption(f"This will distribute {len(teams)} teams equally across {len(current_judges)} judges")
                
                elif teams and not current_judges:
                    st.divider()
                    st.warning("⚠️ Assign judges to this event first before distributing teams")
                
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
    from ai.email_generation import generate_mentor_outreach_email
    
    st.title("🤖 Mentor Matching (AI)")
    st.markdown("*AI-powered student-mentor matching with automated email outreach*")
    st.divider()
    
    # Initialize services
    student_service = StudentService()
    mentor_service = MentorService()
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
    
    # Instant testing button
    if st.button("⚡ Create Mentor Requests (Instant)", use_container_width=True):
        from services.mentoring_service import MentoringService
        mentoring_service = MentoringService()
        
        with st.spinner("Creating mentorship requests..."):
            result = workflow.run_matching_workflow_for_student(
                student_id=student_id,
                top_n=top_n
            )
        
        if result['success']:
            st.toast("Mentor requests created instantly!", icon="⚡")
        else:
            st.error("Failed to create instant requests")
            for error in result['errors']:
                st.warning(f"{error}")
    
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
        
        st.caption(f"Total matches: {len(past_matches)}")
    else:
        st.info("No past matches found for this student.")
    
    # Add AI Email Generation Testing Section
    st.divider()
    st.subheader("✉️ Test AI Email Generation")
    st.caption("Preview the refined email generation before running the full workflow")
    
    col_test1, col_test2 = st.columns(2)
    
    with col_test1:
        # Student selection for testing
        test_students = student_service.list_students()
        if test_students:
            test_student_options = {f"{s.get('name')} ({s.get('major')})": s.get('_id') 
                                   for s in test_students}
            selected_test_student_name = st.selectbox(
                "Select Student for Test",
                options=list(test_student_options.keys()),
                key="test_student_select"
            )
            test_student_id = test_student_options[selected_test_student_name]
            test_student = student_service.get_student_by_id(test_student_id)
    
    with col_test2:
        # Mentor selection for testing
        test_mentors = mentor_service.list_mentors()
        if test_mentors:
            test_mentor_options = {f"{m.get('name')} ({m.get('company')})": m.get('_id') 
                                  for m in test_mentors}
            selected_test_mentor_name = st.selectbox(
                "Select Mentor for Test",
                options=list(test_mentor_options.keys()),
                key="test_mentor_select"
            )
            test_mentor_id = test_mentor_options[selected_test_mentor_name]
            test_mentor = mentor_service.get_mentor_by_id(test_mentor_id)
    
    # Generate test email button
    if test_student and test_mentor:
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("🤖 Generate AI Email", type="primary", use_container_width=True):
                with st.spinner("Generating refined email..."):
                    try:
                        # Create match reason
                        student_interests = ', '.join(test_student.get('interests', [])[:2])
                        mentor_expertise = ', '.join(test_mentor.get('expertise_areas', [])[:2])
                        
                        match_reason = f"{test_student.get('name')} is passionate about {student_interests}, which aligns well with your expertise in {mentor_expertise}. This mentorship could provide valuable guidance as they prepare for their career."
                        
                        # Generate email
                        subject, body = generate_mentor_outreach_email(
                            test_student, 
                            test_mentor, 
                            match_reason
                        )
                        
                        # Store in session state
                        st.session_state['generated_email_subject'] = subject
                        st.session_state['generated_email_body'] = body
                        st.session_state['email_generated'] = True
                        
                        st.success("✅ Email generated successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error generating email: {str(e)}")
        
        with col_btn2:
            if st.session_state.get('email_generated', False):
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state['email_generated'] = False
                    st.session_state.pop('generated_email_subject', None)
                    st.session_state.pop('generated_email_body', None)
                    st.rerun()
        
        # Display generated email
        if st.session_state.get('email_generated', False):
            st.divider()
            
            st.markdown("### 📧 Generated Email Preview")
            
            # Subject
            st.markdown("**Subject:**")
            st.code(st.session_state.get('generated_email_subject', ''), language=None)
            
            # Body
            st.markdown("**Body:**")
            email_body = st.session_state.get('generated_email_body', '')
            
            # Display email content
            st.text_area(
                "Email Content",
                value=email_body,
                height=300,
                disabled=True,
                label_visibility="collapsed"
            )


def render_mentorship_tracker():
    """Render the mentorship tracker showing all mentor-student links"""
    from services.mentoring_service import MentoringService
    
    st.title("👥 Mentorship Tracker")
    st.markdown("Track all mentorship relationships and their statuses.")
    st.markdown("---")
    
    # Initialize service
    mentoring_service = MentoringService()
    
    # Get all mentorship links
    all_links = mentoring_service.get_all_links()
    
    if not all_links:
        st.info("📭 No mentorship relationships have been established yet.")
        st.markdown("")
        st.markdown("Mentorship links will appear here after the matching engine assigns students to mentors.")
        return
    
    # Display summary metrics
    total_links = len(all_links)
    accepted_links = len([link for link in all_links if link.get("status") == "accepted"])
    pending_links = len([link for link in all_links if link.get("status") == "pending"])
    declined_links = len([link for link in all_links if link.get("status") == "declined"])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Links", total_links)
    with col2:
        st.metric("✅ Accepted", accepted_links)
    with col3:
        st.metric("⏳ Pending", pending_links)
    with col4:
        st.metric("❌ Declined", declined_links)
    
    st.markdown("---")
    
    # Create tabs for different statuses
    tab1, tab2, tab3, tab4 = st.tabs(["📊 All Links", "✅ Accepted", "⏳ Pending", "❌ Declined"])
    
    # TAB 1: All Links
    with tab1:
        st.markdown("### All Mentorship Relationships")
        
        # Prepare data for table
        table_data = []
        for link in all_links:
            status_emoji = {
                "accepted": "✅",
                "pending": "⏳",
                "declined": "❌"
            }.get(link.get("status"), "❓")
            
            table_data.append({
                "Student Name": link.get("student_name", "Unknown"),
                "Student Email": link.get("student_email", "N/A"),
                "Mentor Name": link.get("mentor_name", "Unknown"),
                "Mentor Email": link.get("mentor_email", "N/A"),
                "Status": f"{status_emoji} {link.get('status', 'unknown').capitalize()}",
                "Created": str(link.get("created_at", "N/A"))[:19] if link.get("created_at") else "N/A",
                "Updated": str(link.get("updated_at", "N/A"))[:19] if link.get("updated_at") else "N/A"
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        if st.button("📥 Export to CSV", key="export_all"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"mentorship_links_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # TAB 2: Accepted Links
    with tab2:
        accepted_links_data = [link for link in all_links if link.get("status") == "accepted"]
        
        if accepted_links_data:
            st.markdown(f"### ✅ Active Mentorships ({len(accepted_links_data)})")
            
            for link in accepted_links_data:
                with st.expander(f"👤 {link.get('student_name')} ← 🧑‍🏫 {link.get('mentor_name')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Student Information:**")
                        st.write(f"**Name:** {link.get('student_name')}")
                        st.write(f"**Email:** {link.get('student_email')}")
                    
                    with col2:
                        st.markdown("**Mentor Information:**")
                        st.write(f"**Name:** {link.get('mentor_name')}")
                        st.write(f"**Email:** {link.get('mentor_email')}")
                    
                    st.markdown("---")
                    st.markdown("**Match Details:**")
                    st.write(f"**Status:** ✅ Accepted")
                    st.write(f"**Created:** {str(link.get('created_at'))[:19] if link.get('created_at') else 'N/A'}")
                    st.write(f"**Accepted:** {str(link.get('updated_at'))[:19] if link.get('updated_at') else 'N/A'}")
                    
                    if link.get("match_reason"):
                        st.markdown("---")
                        st.markdown("**Match Reason:**")
                        st.write(link.get("match_reason"))
        else:
            st.info("No accepted mentorships yet.")
    
    # TAB 3: Pending Links
    with tab3:
        pending_links_data = [link for link in all_links if link.get("status") == "pending"]
        
        if pending_links_data:
            st.markdown(f"### ⏳ Pending Approvals ({len(pending_links_data)})")
            st.caption("These mentorship requests are awaiting mentor approval.")
            
            for link in pending_links_data:
                st.markdown(f"<div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                st.markdown(f"**Student:** {link.get('student_name')} ({link.get('student_email')})")
                st.markdown(f"**Mentor:** {link.get('mentor_name')} ({link.get('mentor_email')})")
                st.caption(f"Pending since: {str(link.get('created_at'))[:19] if link.get('created_at') else 'N/A'}")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No pending mentorships.")
    
    # TAB 4: Declined Links
    with tab4:
        declined_links_data = [link for link in all_links if link.get("status") == "declined"]
        
        if declined_links_data:
            st.markdown(f"### ❌ Declined Mentorships ({len(declined_links_data)})")
            
            table_data_declined = []
            for link in declined_links_data:
                table_data_declined.append({
                    "Student": f"{link.get('student_name')} ({link.get('student_email')})",
                    "Mentor": f"{link.get('mentor_name')} ({link.get('mentor_email')})",
                    "Declined On": str(link.get("updated_at"))[:19] if link.get("updated_at") else "N/A"
                })
            
            df_declined = pd.DataFrame(table_data_declined)
            st.dataframe(df_declined, use_container_width=True, hide_index=True)
        else:
            st.info("No declined mentorships.")


def render_email_management_page():
    """Render the email management page with history sections"""
    st.title("📧 Email Management")
    
    # Initialize email service
    email_service = EmailService()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📅 Scheduled Emails", "✅ Sent Emails", "❌ Failed Emails"])
    
    # TAB 1: Scheduled Emails (Future Queue)
    with tab1:
        st.subheader("Scheduled Emails (Future Email Queue)")
        st.caption("Emails waiting to be sent at their planned time")
        
        # Immediate send button
        col_send1, col_send2, col_send3 = st.columns([2, 1, 2])
        with col_send2:
            if st.button("🚀 Send All Now", type="primary", use_container_width=True, key="send_scheduled_now"):
                # Get all scheduled emails
                scheduled_to_send = email_service.list_scheduled_emails()
                
                if not scheduled_to_send:
                    st.warning("No scheduled emails to send")
                else:
                    # Send all immediately
                    from services.student_service import StudentService
                    from services.mentor_service import MentorService
                    from services.match_service import MatchService
                    from ai.email_generation import generate_mentor_outreach_email
                    
                    student_service = StudentService()
                    mentor_service = MentorService()
                    match_service = MatchService()
                    
                    success_count = 0
                    failed_count = 0
                    
                    with st.spinner(f"Sending {len(scheduled_to_send)} emails..."):
                        for email_doc in scheduled_to_send:
                            try:
                                # Get match details
                                match_id = email_doc.get('match_id')
                                if not match_id:
                                    failed_count += 1
                                    continue
                                
                                match = match_service.get_match_by_id(match_id)
                                if not match:
                                    failed_count += 1
                                    continue
                                
                                # Get student and mentor
                                student = student_service.get_student_by_id(match.get('student_id'))
                                mentor = mentor_service.get_mentor_by_id(match.get('mentor_id'))
                                
                                if not student or not mentor:
                                    failed_count += 1
                                    continue
                                
                                # Generate and send email
                                subject, body = generate_mentor_outreach_email(
                                    student=student,
                                    mentor=mentor,
                                    match_reason=match.get('match_reason', '')
                                )
                                
                                # Send via n8n webhook
                                send_success, sent_email_id = email_service.send_mentor_match_email(
                                    mentor_email=mentor.get('email'),
                                    mentor_name=mentor.get('name'),
                                    subject=subject,
                                    body=body,
                                    match_id=str(match_id)
                                )
                                
                                if send_success:
                                    # Mark the scheduled email as sent
                                    email_service.mark_email_sent(str(email_doc['_id']))
                                    success_count += 1
                                else:
                                    failed_count += 1
                                    
                            except Exception as e:
                                print(f"Error sending email: {str(e)}")
                                failed_count += 1
                    
                    if success_count > 0:
                        st.success(f"✅ Successfully sent {success_count} email(s) immediately!")
                        st.balloons()
                    
                    if failed_count > 0:
                        st.warning(f"⚠️ {failed_count} email(s) failed to send")
                    
                    import time
                    time.sleep(2)
                    st.rerun()
        
        st.markdown("---")
        
        scheduled_emails = email_service.list_scheduled_emails()
        
        if scheduled_emails:
            st.info(f"📬 {len(scheduled_emails)} email(s) in queue")
            
            # Create table data
            table_data = []
            for email in scheduled_emails:
                planned_time = email.get("planned_send_time")
                if isinstance(planned_time, str):
                    planned_time = datetime.fromisoformat(planned_time.replace('Z', '+00:00'))
                
                table_data.append({
                    "Recipient": email.get("recipient_email", "N/A"),
                    "Subject": email.get("subject", "N/A"),
                    "Planned Send Time": planned_time.strftime("%b %d, %Y %I:%M %p") if planned_time else "N/A",
                    "Status": "📅 Scheduled"
                })
            
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("✨ No emails scheduled. The queue is empty.")
    
    # TAB 2: Sent Emails (History)
    with tab2:
        st.subheader("🟩 Sent Emails (History)")
        st.caption("Successfully delivered emails")
        
        sent_emails = email_service.list_sent_emails(limit=50)
        
        if sent_emails:
            st.success(f"✅ {len(sent_emails)} email(s) sent successfully")
            
            # Create table data
            table_data = []
            for email in sent_emails:
                planned_time = email.get("planned_send_time")
                actual_time = email.get("actual_send_time") or email.get("sent_at")
                
                if isinstance(planned_time, str):
                    planned_time = datetime.fromisoformat(planned_time.replace('Z', '+00:00'))
                if isinstance(actual_time, str):
                    actual_time = datetime.fromisoformat(actual_time.replace('Z', '+00:00'))
                
                table_data.append({
                    "Recipient": email.get("recipient_email", "N/A"),
                    "Subject": email.get("subject", "N/A"),
                    "Planned Send Time": planned_time.strftime("%b %d, %Y %I:%M %p") if planned_time else "N/A",
                    "Actual Send Time": actual_time.strftime("%b %d, %Y %I:%M %p") if actual_time else "Legacy (pre-tracking)",
                    "Status": "✅ Sent"
                })
            
            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📭 No emails sent yet.")
    
    # TAB 3: Failed Emails (Error Log)
    with tab3:
        st.subheader("🟥 Failed Emails (Error Log)")
        st.caption("Emails that encountered delivery errors")
        
        failed_emails = email_service.list_failed_emails(limit=50)
        
        if failed_emails:
            st.error(f"⚠️ {len(failed_emails)} email(s) failed to send")
            
            # Create table data with color coding
            for i, email in enumerate(failed_emails):
                with st.expander(f"❌ {email.get('recipient_email', 'N/A')} - {email.get('subject', 'N/A')}", expanded=(i < 3)):
                    planned_time = email.get("planned_send_time")
                    failure_time = email.get("actual_send_time")
                    
                    if isinstance(planned_time, str):
                        planned_time = datetime.fromisoformat(planned_time.replace('Z', '+00:00'))
                    if isinstance(failure_time, str):
                        failure_time = datetime.fromisoformat(failure_time.replace('Z', '+00:00'))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Recipient:**", email.get("recipient_email", "N/A"))
                        st.write("**Subject:**", email.get("subject", "N/A"))
                        st.write("**Planned Send Time:**", planned_time.strftime("%b %d, %Y %I:%M %p") if planned_time else "N/A")
                    with col2:
                        st.write("**Failure Time:**", failure_time.strftime("%b %d, %Y %I:%M %p") if failure_time else "Legacy (pre-tracking)")
                        st.write("**Error Message:**")
                        st.code(email.get("error_message", "Unknown error"), language=None)
        else:
            st.success("✅ No failed emails. All deliveries successful!")


def main():
    """Main application entry point"""
    from views.student_dashboard_view import render_student_dashboard
    from views.mentor_dashboard_view import render_mentor_dashboard
    
    # Initialize the app
    init_app()
    
    # Check authentication
    if not st.session_state.get("authenticated", False):
        render_login_page()
        return
    
    # Get user role
    role = st.session_state.get("role", "admin")
    
    # Route based on role
    if role == "student":
        # Student dashboard - no sidebar navigation
        render_student_dashboard()
        return
    
    elif role == "mentor":
        # Mentor dashboard - no sidebar navigation
        render_mentor_dashboard()
        return
    
    # Admin role - existing behavior (DO NOT BREAK)
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render the selected page
    if page == "🗂️ Dashboard":
        render_dashboard()
    elif page == "🎓 Students":
        render_students_page()
    elif page == "🧑‍🏫 Mentors":
        render_mentors_page()
    elif page == "📅 Events":
        render_events_page()
    elif page == "🏆 Case Competitions":
        render_case_competitions_page()
    elif page == "🤖 Matching":
        render_matching_page()
    elif page == "👥 Mentorship Tracker":
        render_mentorship_tracker()
    elif page == "📨 Email Management":
        render_email_management_page()


if __name__ == "__main__":
    main()
