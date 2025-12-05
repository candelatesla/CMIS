"""
My Assigned Mentor Page for Student Dashboard
"""
import streamlit as st
from services.mentoring_service import MentoringService
from services.mentor_service import MentorService


def render_mentor_match(student):
    """Render the mentor match page showing assigned mentor details"""
    
    # Use 9-digit student_id if available, otherwise fall back to _id
    student_id = student.get("student_id") or str(student.get("_id"))
    
    # Get services
    mentoring_service = MentoringService()
    mentor_service = MentorService()
    
    # ============ MY ASSIGNED MENTOR ============
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🧑‍🏫 Your Assigned Mentor")
    
    # Fetch mentor via mentoring service
    mentor = mentoring_service.get_student_mentor(student_id)
    
    if not mentor:
        st.info("🔍 You do not have an assigned mentor yet. Please check back later or contact your program administrator.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Get mentorship status
    mentorship_status = mentor.get("mentorship_status", "unknown")
    match_reason = mentor.get("match_reason", "")
    matched_at = mentor.get("matched_at")
    
    # Display status based on mentorship status
    if mentorship_status == "accepted":
        st.markdown("<div style='background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("### ✅ Active Mentorship")
        st.markdown(f"**Your mentor has accepted your match!** You can now reach out to {mentor.get('name', 'your mentor')} to schedule meetings.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif mentorship_status == "pending":
        st.markdown("<div style='background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin-bottom: 20px;'>", unsafe_allow_html=True)
        st.markdown("### ⏳ Mentorship Request Pending")
        st.markdown(f"**Your mentorship request is awaiting approval from {mentor.get('name', 'your mentor')}.**")
        st.markdown("You'll be notified once they accept. In the meantime, you can review their profile below.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        st.warning(f"⚠️ **Status:** {mentorship_status.capitalize()}")
    
    st.markdown("---")
    
    # ============ MENTOR INFORMATION ============
    st.markdown("### 👤 Mentor Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Name**")
        st.write(mentor.get('name', 'N/A'))
        
        st.markdown("**Email**")
        st.write(mentor.get('email', 'N/A'))
        
        st.markdown("**Company**")
        st.write(mentor.get('company', 'N/A'))
        
        st.markdown("**Job Title**")
        st.write(mentor.get('job_title', 'N/A'))
    
    with col2:
        st.markdown("**Industry**")
        st.write(mentor.get('industry', 'N/A'))
        
        st.markdown("**Years of Experience**")
        years_exp = mentor.get('years_of_experience', 'N/A')
        st.write(f"{years_exp} years" if isinstance(years_exp, (int, float)) else years_exp)
        
        st.markdown("**Expertise Areas**")
        expertise = mentor.get('expertise_areas', [])
        if expertise:
            st.write(", ".join(expertise))
        else:
            st.write("N/A")
        
        st.markdown("**Interests**")
        interests = mentor.get('interests', [])
        if interests:
            st.write(", ".join(interests))
        else:
            st.write("N/A")
    
    st.markdown("---")
    
    # ============ MATCH REASON ============
    if match_reason:
        with st.expander("💡 Why you were matched", expanded=True):
            st.markdown(match_reason)
    else:
        st.info("ℹ️ Match reason not available.")
    
    # Show matched timestamp
    if matched_at:
        st.caption(f"Matched on: {str(matched_at)[:19]}")
    
    st.markdown("---")
    
    # ============ MENTOR RESUME (COLLAPSIBLE) ============
    mentor_resume = mentor.get('resume_text', '')
    
    if mentor_resume:
        with st.expander("📄 Mentor Resume / Background"):
            st.text_area(
                "Resume Text",
                value=mentor_resume,
                height=300,
                disabled=True,
                label_visibility="collapsed"
            )
    
    st.markdown("---")
    
    # ============ CONTACT INFORMATION ============
    st.markdown("### 📨 Contact Your Mentor")
    
    st.markdown(f"""
    **Email:** [{mentor.get('email', 'N/A')}](mailto:{mentor.get('email', '')})
    
    Feel free to reach out to your mentor to schedule a meeting or ask questions about your career goals.
    """)
    
    st.markdown("---")
    
    # ============ FUTURE FEATURES (PLACEHOLDER) ============
    st.markdown("### 🚀 Coming Soon")
    
    col_future1, col_future2 = st.columns(2)
    
    with col_future1:
        st.markdown("**📧 Upcoming Outreach Emails**")
        st.text("Scheduled check-ins and follow-ups")
        st.caption("🚧 Feature in development")
    
    with col_future2:
        st.markdown("**📊 Match Progress Tracker**")
        st.text("Track meetings and mentorship progress")
        st.caption("🚧 Feature in development")
    
    st.markdown("</div>", unsafe_allow_html=True)
