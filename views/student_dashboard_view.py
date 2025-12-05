"""
Student Dashboard View
View function for authenticated students (not a Streamlit page)
"""
import streamlit as st
from services.student_service import StudentService
from views.student_pages import (
    render_edit_profile,
    render_events_and_teams,
    render_scores,
    render_mentor_match
)


def render_student_dashboard():
    """Render the student dashboard with sidebar navigation"""
    
    # Get student info from session
    student_id = st.session_state.get("linked_student_id")
    email = st.session_state.get("email")
    
    if not student_id:
        st.error("❌ No student profile linked to this account.")
        return
    
    # Get student service
    student_service = StudentService()
    
    # Fetch student data
    student = student_service.get_student_by_id(student_id)
    
    if not student or "error" in student:
        st.error("❌ Student profile not found.")
        return
    
    # Dashboard header
    st.title("🎓 Student Dashboard")
    st.markdown(f"### Welcome, {student.get('name', 'Student')}!")
    st.markdown("---")
    
    # ============ SIDEBAR NAVIGATION ============
    with st.sidebar:
        st.markdown("### 📘 Student Menu")
        selected_page = st.radio(
            "Navigate",
            [
                "Edit Profile",
                "Event Registration & Teams",
                "My Scores",
                "My Assigned Mentor"
            ],
            key="student_nav"
        )
        
        st.markdown("---")
        
        # Logout button in sidebar
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # ============ PAGE ROUTING ============
    if selected_page == "Edit Profile":
        render_edit_profile(student)
    
    elif selected_page == "Event Registration & Teams":
        render_events_and_teams(student)
    
    elif selected_page == "My Scores":
        render_scores(student)
    
    elif selected_page == "My Assigned Mentor":
        render_mentor_match(student)

