"""
Mentor Dashboard View
View function for authenticated mentors (not a Streamlit page)
"""
import streamlit as st
from services.mentor_service import MentorService
from views.judge_pages import (
    render_judge_edit_profile,
    render_assigned_teams,
    render_score_teams,
    render_mentoring_students,
    render_mentor_requests
)


def render_mentor_dashboard():
    """Render the mentor/judge dashboard with sidebar navigation"""
    
    # Get mentor info from session
    mentor_id = st.session_state.get("linked_mentor_id")
    email = st.session_state.get("email")
    
    if not mentor_id:
        st.error("❌ No mentor profile linked to this account.")
        return
    
    # Get mentor service
    mentor_service = MentorService()
    
    # Fetch mentor data
    mentor = mentor_service.get_mentor_by_id(mentor_id)
    
    if not mentor or "error" in mentor:
        st.error("❌ Mentor profile not found.")
        return
    
    # Dashboard header
    st.title("🧑‍⚖️ Judge / Mentor Dashboard")
    st.markdown(f"### Welcome, {mentor.get('name', 'Mentor')}!")
    st.markdown("---")
    
    # ============ SIDEBAR NAVIGATION ============
    with st.sidebar:
        st.markdown("### 🧑‍⚖️ Judge Menu")
        selected_page = st.radio(
            "Navigate",
            [
                "Edit Profile",
                "Assigned Teams",
                "Score Teams",
                "Mentor Requests",
                "Students You Mentor"
            ],
            key="judge_nav"
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
        render_judge_edit_profile(mentor)
    
    elif selected_page == "Assigned Teams":
        render_assigned_teams(mentor)
    
    elif selected_page == "Score Teams":
        render_score_teams(mentor)
    
    elif selected_page == "Mentor Requests":
        render_mentor_requests(mentor)
    
    elif selected_page == "Students You Mentor":
        render_mentoring_students(mentor)
